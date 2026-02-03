"""Document processing endpoints."""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.core.exceptions import ApplicationException
from app.core.logger import get_logger
from app.core.security import UPLOAD_TEMP_DIR
from app.models.schemas import (
    CVAnalysisResponse, 
    AnalyzeDocumentsRequest, 
    AnalyzeDocumentsResponse,
    ComparisonResult,
    TalentSummary,
    MatchBreakdown,
    ExtractedAttributesSimple,
    SkillCount,
    LocationCount
)
from app.services.cv_extractor import CVExtractor
from app.services.pdf_processor import PDFProcessor
from app.utils.file_handler import generate_document_id, save_uploaded_file
from app.utils.validators import validate_document_file

logger = get_logger(__name__)
router = APIRouter()


def _split_semicolon(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(";") if v.strip()]


def _get_attr_value(attrs: List[Dict], attr_type: str) -> Optional[str]:
    best: Optional[Tuple[float, str]] = None
    for a in attrs:
        if a.get("attribute_type") != attr_type:
            continue
        val = a.get("value")
        if val is None:
            continue
        conf = float(a.get("confidence", 0.0) or 0.0)
        if best is None or conf > best[0]:
            best = (conf, str(val))
    return best[1] if best else None


def _is_generic_filename_stem(stem: str) -> bool:
    low = stem.lower().strip()
    if not low:
        return True
    if any(ch.isdigit() for ch in low):
        return True
    if any(sep in low for sep in {"_", "-"}):
        # common temp names like prueba-1, cv_juan, etc.
        # we'll still allow if it looks like a real name later.
        pass
    generic_tokens = {
        "cv",
        "curriculum",
        "curriculum vitae",
        "hoja de vida",
        "resume",
        "perfil",
        "documento",
        "prueba",
        "pruebas",
        "archivo",
    }
    return any(tok == low or tok in low for tok in generic_tokens)


def _extract_candidate_name(raw_text: str, filename: str, document_id: str) -> str:
    stem = Path(filename).stem.strip()

    # Prefer filename only if it really looks like a person's name.
    if stem and not _is_generic_filename_stem(stem):
        # allow spaces, letters, accents, dots and apostrophes
        if re.match(r"^[A-Za-zÁÉÍÓÚÑáéíóúñ.'\- ]+$", stem) and 3 <= len(stem) <= 60:
            words = [w for w in stem.split() if w]
            if 2 <= len(words) <= 5:
                return stem

    skip_tokens = {
        "curriculum",
        "curriculum vitae",
        "hoja de vida",
        "resume",
        "cv",
        "perfil",
        "experiencia",
        "education",
        "skills",
        "habilidades",
        "contacto",
        "linkedin",
    }

    def is_name_line(line: str) -> bool:
        if not line:
            return False
        low = line.lower()
        if any(tok in low for tok in skip_tokens):
            return False
        if "@" in line or "http" in low:
            return False
        if any(ch.isdigit() for ch in line):
            return False
        if len(line) > 80:
            return False
        words = [w for w in re.split(r"\s+", line) if w]
        if not (1 <= len(words) <= 5):
            return False
        for w in words:
            if not re.match(r"^[A-Za-zÁÉÍÓÚÑáéíóúñ.'\-]+$", w):
                return False
        # allow all-caps or Title Case
        return True

    lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
    head = lines[:15]
    for i, ln in enumerate(head):
        if not is_name_line(ln):
            continue

        # Combine with next line if it also looks like a name (common PDFs split name across lines)
        if i + 1 < len(head) and is_name_line(head[i + 1]):
            combined = f"{ln} {head[i + 1]}".strip()
            words = [w for w in combined.split() if w]
            if 2 <= len(words) <= 5 and len(combined) <= 80:
                return combined

        # Or extract a leading name prefix from longer lines
        prefix = re.match(
            r"^([A-Za-zÁÉÍÓÚÑáéíóúñ.'\-]+(?:\s+[A-Za-zÁÉÍÓÚÑáéíóúñ.'\-]+){1,4})\b",
            ln,
        )
        if prefix:
            candidate = prefix.group(1).strip()
            words = [w for w in candidate.split() if w]
            if 2 <= len(words) <= 5 and 3 <= len(candidate) <= 80:
                return candidate

    return f"Candidato {document_id[:4]}"


def _build_cv_warnings(raw_text: str, extracted_attrs: List[Dict]) -> List[str]:
    warnings: List[str] = []
    low_text = raw_text.lower()

    role = _get_attr_value(extracted_attrs, "role")
    location = _get_attr_value(extracted_attrs, "location")
    years_exp = _get_attr_value(extracted_attrs, "years_experience")

    if not years_exp:
        warnings.append("EXPERIENCE_NOT_FOUND: No fue posible extraer años de experiencia")

    if not role:
        warnings.append("ROLE_NOT_FOUND: No fue posible extraer el rol del candidato")
    else:
        if role.lower() not in low_text:
            warnings.append(f"ROLE_UNVERIFIED: Rol detectado ('{role}') no pudo verificarse en el texto del CV")
        else:
            # weak context check
            cue_words = {"cargo", "rol", "posición", "posicion", "perfil", "puesto", "ocupación", "ocupacion"}
            idx = low_text.find(role.lower())
            if idx >= 0:
                window = low_text[max(0, idx - 80) : idx + 120]
                if not any(cue in window for cue in cue_words):
                    warnings.append(
                        f"ROLE_WEAK_CONTEXT: Rol ('{role}') aparece sin contexto claro de cargo/rol en el CV"
                    )

    if not location:
        warnings.append("LOCATION_NOT_FOUND: No fue posible extraer la ubicación del candidato")
    else:
        if location.lower() not in low_text:
            warnings.append(
                f"LOCATION_UNVERIFIED: Ubicación detectada ('{location}') no pudo verificarse en el texto del CV"
            )
        else:
            cue_words = {"residencia", "ubicación", "ubicacion", "ciudad", "dirección", "direccion", "domicilio", "vive"}
            loc_low = location.lower()
            found_any = False
            start = 0
            while True:
                idx = low_text.find(loc_low, start)
                if idx < 0:
                    break
                window = low_text[max(0, idx - 80) : idx + 120]
                if any(cue in window for cue in cue_words):
                    found_any = True
                    break
                start = idx + len(loc_low)
            if not found_any:
                warnings.append(
                    f"LOCATION_WEAK_CONTEXT: Ubicación ('{location}') aparece sin contexto claro de residencia/ubicación"
                )

    return warnings


def _sanitize_extracted_attributes(raw_text: str, extracted_attrs: List[Dict]) -> Tuple[List[Dict], List[str]]:
    warnings = _build_cv_warnings(raw_text, extracted_attrs)
    low_text = raw_text.lower()

    role = _get_attr_value(extracted_attrs, "role")
    location = _get_attr_value(extracted_attrs, "location")

    drop_role = bool(role and role.lower() not in low_text)

    # Location can be present in the CV text but not actually describe residence.
    # If context is weak, prefer hiding the location to avoid misleading UI.
    location_weak = any(w.startswith("LOCATION_WEAK_CONTEXT") for w in warnings)
    drop_location = bool(location and (location.lower() not in low_text or location_weak))

    if not drop_role and not drop_location:
        return extracted_attrs, warnings

    sanitized: List[Dict] = []
    for a in extracted_attrs:
        t = a.get("attribute_type")
        if drop_role and t == "role":
            continue
        if drop_location and t == "location":
            continue
        sanitized.append(a)
    return sanitized, warnings


@router.post(
    "/upload",
    response_model=List[CVAnalysisResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload and analyze CV documents",
)
async def upload_documents(files: List[UploadFile] = File(..., description="List of CV files to upload")):
    """Upload and analyze multiple CV documents."""
    try:
        if not files:
             raise HTTPException(status_code=400, detail="No files provided")

        results = []

        for file in files:
            try:
                file_content = await file.read()
                validate_document_file(file.filename, len(file_content))

                document_id = generate_document_id()
                filepath = save_uploaded_file(file_content, file.filename, document_id)

                raw_text = PDFProcessor.extract_text(filepath)
                text_preview = PDFProcessor.get_text_preview(raw_text)
                attributes = CVExtractor.extract_attributes(raw_text, document_id)
                attributes, warnings = _sanitize_extracted_attributes(raw_text, attributes)

                result = CVAnalysisResponse(
                    document_id=document_id,
                    filename=file.filename,
                    status="success",
                    extracted_attributes=attributes,
                    raw_text_preview=text_preview,
                    warnings=warnings,
                    processing_time_ms=0.0,
                )
                results.append(result)
                logger.info(f"Successfully analyzed document: {file.filename}")

            except ApplicationException as e:
                result = CVAnalysisResponse(
                    document_id="",
                    filename=file.filename,
                    status="error",
                    error_message=e.message,
                    processing_time_ms=0.0,
                )
                results.append(result)
                logger.error(f"Error analyzing {file.filename}: {e.message}")

        return results

    except Exception as e:
        logger.error(f"Unexpected error in upload_documents: {str(e)}")
        raise HTTPException(status_code=500, detail={"error": "INTERNAL_ERROR", "message": str(e)})


@router.post(
    "/analyze",
    response_model=AnalyzeDocumentsResponse,
    summary="Analyze documents against job requirements",
)
async def analyze_documents(request: AnalyzeDocumentsRequest):
    """Analyze uploaded documents against job requirements."""
    try:
        def extract_email(raw_text: str) -> Optional[str]:
            m = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", raw_text)
            return m.group(0) if m else None

        def extract_phone(raw_text: str) -> Optional[str]:
            # Very loose phone heuristic; keeps the first plausible sequence.
            m = re.search(r"(\+?\d[\d\s().-]{7,}\d)", raw_text)
            if not m:
                return None
            phone = re.sub(r"\s+", " ", m.group(1)).strip()
            return phone

        results = []
        total_experience = 0
        role_matches = 0
        all_skills = []
        all_locations = []

        for doc_id in request.documentIds:
            # 1. Recuperar documento (re-procesar)
            doc_dir = Path(UPLOAD_TEMP_DIR) / doc_id
            if not doc_dir.exists():
                continue
            
            files = list(doc_dir.glob("*"))
            if not files:
                continue
                
            filepath = files[0]
            raw_text = PDFProcessor.extract_text(filepath)

            extracted_attrs = CVExtractor.extract_attributes(raw_text, doc_id)
            extracted_attrs, warnings = _sanitize_extracted_attributes(raw_text, extracted_attrs)

            extracted_role = _get_attr_value(extracted_attrs, "role")
            extracted_location = _get_attr_value(extracted_attrs, "location")
            extracted_skills = _split_semicolon(_get_attr_value(extracted_attrs, "skills"))
            extracted_languages = _split_semicolon(_get_attr_value(extracted_attrs, "languages"))
            years_exp_str = _get_attr_value(extracted_attrs, "years_experience")
            years_exp: Optional[int] = None
            if years_exp_str is not None and str(years_exp_str).strip():
                try:
                    years_exp = int(float(str(years_exp_str).strip()))
                except Exception:
                    years_exp = None

            candidate_name = _extract_candidate_name(raw_text, filepath.name, doc_id)
            email = extract_email(raw_text)
            phone = extract_phone(raw_text)

            concerns: List[str] = []

            # Surface warnings as user-facing concerns too (keeps UI consistent even if it only shows concerns).
            # We keep the coded warnings separately in ComparisonResult.warnings.
            for w in warnings:
                # Keep message after the first colon if present.
                msg = w.split(":", 1)[1].strip() if ":" in w else w
                concerns.append(msg)

            # Basic verification to avoid showing misleading values when extraction is wrong.
            # If we cannot verify, we prefer returning "No especificado" + a concern.
            if extracted_role and extracted_role.lower() not in raw_text.lower():
                concerns.append(
                    f"Rol detectado ('{extracted_role}') no pudo verificarse en el texto del CV"
                )
                extracted_role = None
            if extracted_location and extracted_location.lower() not in raw_text.lower():
                concerns.append(
                    f"Ubicación detectada ('{extracted_location}') no pudo verificarse en el texto del CV"
                )
                extracted_location = None
            if not extracted_role:
                concerns.append("No fue posible extraer/verificar el rol del candidato")
            if years_exp is None:
                concerns.append("No fue posible extraer años de experiencia")

            extracted_data = ExtractedAttributesSimple(
                candidateName=candidate_name,
                email=email,
                phone=phone,
                location=extracted_location,
                role=extracted_role or "No especificado",
                yearsExperience=years_exp,
                skills=extracted_skills,
                languages=extracted_languages,
                education=[],
                certifications=[],
            )

            # 2. Calcular Score (Lógica simple de coincidencia)
            reqs = request.jobRequirements
            
            # Skills match
            req_skills_lower = {rs.lower() for rs in (reqs.requiredSkills or [])}
            matched_skills = [s for s in extracted_data.skills if s.lower() in req_skills_lower]
            skills_score = (len(matched_skills) / len(reqs.requiredSkills)) * 100 if reqs.requiredSkills else 100
            
            # Experience match
            if reqs.minExperience > 0:
                if extracted_data.yearsExperience is None:
                    exp_score = 0
                else:
                    exp_score = (
                        100
                        if extracted_data.yearsExperience >= reqs.minExperience
                        else (extracted_data.yearsExperience / reqs.minExperience) * 100
                    )
            else:
                exp_score = 100

            # Location match
            if reqs.location:
                loc_score = 100 if (extracted_data.location or "").lower().find(reqs.location.lower()) >= 0 else 0
            else:
                loc_score = 100

            # Languages match
            if reqs.languages:
                req_lang_lower = {l.lower() for l in (reqs.languages or [])}
                matched_langs = [l for l in extracted_data.languages if l.lower() in req_lang_lower]
                lang_score = (len(matched_langs) / len(reqs.languages)) * 100 if reqs.languages else 100
            else:
                lang_score = 100

            edu_score = 100

            # Overall score (simple weighting; still deterministic)
            filters = request.filters
            weights = {
                "skills": 0.55 if filters.prioritizeSkills else 0.35,
                "experience": 0.35 if filters.prioritizeExperience else 0.20,
                "location": 0.05 if filters.prioritizeLocation else 0.0,
                "languages": 0.05 if filters.prioritizeLanguages else 0.0,
                "education": 0.0,
            }
            total_w = sum(weights.values()) or 1.0
            overall_score = (
                skills_score * (weights["skills"] / total_w)
                + exp_score * (weights["experience"] / total_w)
                + loc_score * (weights["location"] / total_w)
                + lang_score * (weights["languages"] / total_w)
                + edu_score * (weights["education"] / total_w)
            )

            comparison = ComparisonResult(
                documentId=doc_id,
                candidateName=extracted_data.candidateName,
                attributes=extracted_data,
                overallScore=overall_score,
                matchBreakdown=MatchBreakdown(
                    skillsMatch=skills_score,
                    experienceMatch=exp_score,
                    locationMatch=loc_score,
                    languagesMatch=lang_score,
                    educationMatch=edu_score
                ),
                matchedSkills=matched_skills,
                missingSkills=[s for s in reqs.requiredSkills if s.lower() not in [ms.lower() for ms in matched_skills]],
                highlights=["Experiencia relevante", "Coincidencia de habilidades"],
                concerns=concerns,
                warnings=warnings,
            )
            
            results.append(comparison)
            
            # Stats aggregation
            if extracted_data.yearsExperience is not None:
                total_experience += extracted_data.yearsExperience
            all_skills.extend(extracted_data.skills)
            if extracted_data.location:
                all_locations.append(extracted_data.location)

        # Construir resumen
        from collections import Counter
        skill_counts = [SkillCount(skill=k, count=v) for k, v in Counter(all_skills).most_common(5)]
        loc_counts = [LocationCount(location=k, count=v) for k, v in Counter(all_locations).most_common(5)]

        summary = TalentSummary(
            totalCandidates=len(results),
            matchesByRole=len(results), # Simplificado
            averageExperience=total_experience / len([r for r in results if r.attributes.yearsExperience is not None])
            if any(r.attributes.yearsExperience is not None for r in results)
            else 0,
            topSkills=skill_counts,
            locationDistribution=loc_counts
        )

        return AnalyzeDocumentsResponse(results=results, summary=summary)

    except Exception as e:
        logger.error(f"Error in analyze_documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}", response_model=CVAnalysisResponse)
async def get_document_analysis(document_id: str):
    # ... (Mismo código que te pasé antes para GET)
    try:
        doc_dir = Path(UPLOAD_TEMP_DIR) / document_id
        if not doc_dir.exists() or not doc_dir.is_dir():
            raise HTTPException(status_code=404, detail="Document not found")
        files = list(doc_dir.glob("*"))
        if not files:
            raise HTTPException(status_code=404, detail="Document file missing")
        filepath = files[0]
        
        raw_text = PDFProcessor.extract_text(filepath)
        text_preview = PDFProcessor.get_text_preview(raw_text)
        attributes = CVExtractor.extract_attributes(raw_text, document_id)
        attributes, warnings = _sanitize_extracted_attributes(raw_text, attributes)
        
        return CVAnalysisResponse(
            document_id=document_id,
            filename=filepath.name,
            status="success",
            extracted_attributes=attributes,
            raw_text_preview=text_preview,
            warnings=warnings,
            processing_time_ms=0.0,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error retrieving document")


@router.get(
    "/{document_id}/file",
    summary="Download/view original uploaded CV file",
    responses={
        200: {"description": "The original document file"},
        404: {"description": "Document not found"},
    },
)
async def get_document_file(document_id: str):
    """Return the original uploaded file for a given document_id."""
    doc_dir = Path(UPLOAD_TEMP_DIR) / document_id
    if not doc_dir.exists() or not doc_dir.is_dir():
        raise HTTPException(status_code=404, detail="Document not found")

    files = list(doc_dir.glob("*"))
    if not files:
        raise HTTPException(status_code=404, detail="Document file missing")

    filepath = files[0]
    ext = filepath.suffix.lower()
    media_type = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".doc": "application/msword",
        ".txt": "text/plain",
    }.get(ext, "application/octet-stream")

    return FileResponse(
        path=str(filepath),
        media_type=media_type,
        filename=filepath.name,
        content_disposition_type="inline",
    )

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: str):
    try:
        doc_dir = Path(UPLOAD_TEMP_DIR) / document_id
        if doc_dir.exists():
            import shutil
            shutil.rmtree(doc_dir)
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error deleting document")