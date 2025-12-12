"""CV attribute extraction service."""

from typing import Dict, List, Optional
from pathlib import Path

from app.core.logger import get_logger

logger = get_logger(__name__)

# Integración con NLP existente - con manejo de errores
try:
    from NLP.src.spacy_utils import get_doc
    from NLP.src.parser import _detect_role, _detect_skills
    from NLP.src.extract_rules import (
        extract_experience,
        extract_languages,
        extract_location,
    )
    NLP_AVAILABLE = True
except ImportError as e:
    logger.warning(f"NLP module not available: {e}. Using fallback extraction.")
    NLP_AVAILABLE = False


class CVExtractor:
    """Robustly extracts attributes from CVs using NLP."""

    @staticmethod
    def extract_attributes(cv_text: str, document_id: str) -> List[Dict]:
        """
        Extract key attributes from CV text.
        
        Args:
            cv_text: Raw text extracted from CV
            document_id: Document identifier
            
        Returns:
            List of extracted attributes with confidence scores
        """
        if not NLP_AVAILABLE:
            logger.warning("Using fallback extraction (NLP not available)")
            return CVExtractor._fallback_extraction(cv_text)
        
        try:
            # 1. Crear spaCy doc para procesamiento NLP
            doc = get_doc(cv_text)
            noun_chunks = [chunk.text for chunk in doc.noun_chunks] if hasattr(doc, 'noun_chunks') else []
            
            # 2. Extraer atributos usando catálogos
            extracted = {
                "role": _detect_role(cv_text, noun_chunks),
                "skills": _detect_skills(cv_text, noun_chunks),
                "years_experience": extract_experience(cv_text),
                "languages": extract_languages(cv_text),
                "location": extract_location(cv_text),
                "document_id": document_id,
            }
            
            # 3. Convertir a lista de ExtractedAttribute format
            attributes = []
            
            if extracted["role"]:
                attributes.append({
                    "attribute_type": "role",
                    "value": str(extracted["role"]),
                    "confidence": 0.85,
                    "source_text": None
                })
            
            if extracted["skills"]:
                skills_str = "; ".join(extracted["skills"]) if isinstance(extracted["skills"], list) else str(extracted["skills"])
                attributes.append({
                    "attribute_type": "skills",
                    "value": skills_str,
                    "confidence": 0.8,
                    "source_text": None
                })
            
            if extracted["years_experience"]:
                attributes.append({
                    "attribute_type": "years_experience",
                    "value": str(extracted["years_experience"]),
                    "confidence": 0.9,
                    "source_text": None
                })
            
            if extracted["languages"]:
                langs_str = "; ".join(extracted["languages"]) if isinstance(extracted["languages"], list) else str(extracted["languages"])
                attributes.append({
                    "attribute_type": "languages",
                    "value": langs_str,
                    "confidence": 0.75,
                    "source_text": None
                })
            
            if extracted["location"]:
                attributes.append({
                    "attribute_type": "location",
                    "value": str(extracted["location"]),
                    "confidence": 0.8,
                    "source_text": None
                })
            
            logger.info(f"Extracted {len(attributes)} attributes for document {document_id}")
            return attributes
            
        except Exception as e:
            logger.error(f"Error extracting attributes with NLP: {str(e)}")
            return CVExtractor._fallback_extraction(cv_text)

    @staticmethod
    def _fallback_extraction(cv_text: str) -> List[Dict]:
        """
        Fallback extraction when NLP is not available.
        
        Uses simple pattern matching and keyword detection.
        """
        attributes = []
        
        # Detectar años de experiencia (buscar patrones como "5 años", "10+ años")
        import re
        exp_match = re.search(r'(\d+)\s*\+?\s*(?:años|years)', cv_text.lower())
        if exp_match:
            attributes.append({
                "attribute_type": "years_experience",
                "value": exp_match.group(1),
                "confidence": 0.6,
                "source_text": None
            })
        
        # Detectar ubicación (ciudades comunes de Colombia)
        cities = ["Bogotá", "Medellín", "Cali", "Barranquilla", "Cartagena", "Bogota"]
        for city in cities:
            if city.lower() in cv_text.lower():
                attributes.append({
                    "attribute_type": "location",
                    "value": city,
                    "confidence": 0.6,
                    "source_text": None
                })
                break
        
        # Detectar idiomas comunes
        languages = ["Spanish", "English", "Español", "Inglés"]
        found_langs = [lang for lang in languages if lang.lower() in cv_text.lower()]
        if found_langs:
            attributes.append({
                "attribute_type": "languages",
                "value": "; ".join(found_langs),
                "confidence": 0.5,
                "source_text": None
            })
        
        logger.info(f"Fallback extraction: {len(attributes)} attributes found")
        return attributes