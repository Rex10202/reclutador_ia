from typing import List, Dict, Any, Optional

import joblib
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel

from .config import MODEL_PATH
from .db import get_connection, get_all_candidates
from .features import build_structured_features, features_to_vector


_model_bundle = joblib.load(MODEL_PATH)
MODEL = _model_bundle["model"]
FEATURE_ORDER = _model_bundle["feature_order"]

app = FastAPI(
    title="Recomendador de Candidatos para Talento Humano",
    description="Herramienta web basada en IA que recomienda candidatos a partir de consultas estructuradas.",
    version="0.2.1",
)


class ConsultaEstructuradaReq(BaseModel):
    """
    Representa la "consulta" que recibe el modelo: los requisitos de la vacante.
    """
    role: str
    skills: str
    languages: Optional[str] = None
    experience_years: Optional[float] = 0
    location: Optional[str] = None
    num_candidates: Optional[int] = 10


class CandidatoResp(BaseModel):
    id: int
    nombre: str
    cargo: str
    habilidades: str
    experiencia_anios: int
    idiomas: str
    ubicacion: str
    modalidad: str
    disponibilidad: str
    score: float

class RespuestaRecomendacion(BaseModel):
    consulta: Dict[str, Any]
    candidatos: List[CandidatoResp]

def parse_skills(skills_str: str) -> List[str]:
    if not isinstance(skills_str, str):
        return []
    return [s.strip() for s in skills_str.split(";") if s.strip()]

def parse_idiomas(lang_str: Optional[str]) -> List[str]:
    if not isinstance(lang_str, str) or not lang_str.strip():
        return []
    lang = lang_str.strip().lower()
    if "ingles" in lang:
        return ["Inglés"]
    if "espanol" in lang or "español" in lang:
        return ["Español"]
    if "frances" in lang or "francés" in lang:
        return ["Francés"]
    if "portugues" in lang or "portugués" in lang:
        return ["Portugués"]
    return [lang_str.strip()]


def requisitos_desde_consulta(req: ConsultaEstructuradaReq) -> Dict[str, Any]:
    skills_list = parse_skills(req.skills)
    idiomas_list = parse_idiomas(req.languages)
    exp_years = req.experience_years or 0
    ubicacion = (req.location or "").strip()
    num_cand = req.num_candidates or 10

    requisitos = {
        "cargo": req.role,
        "habilidades": skills_list,
        "idiomas": idiomas_list,
        "experiencia_minima": int(exp_years),
        "ubicacion": ubicacion,
        "modalidad": "",  # podría añadirse si el formulario lo incluye
        "cantidad_candidatos": num_cand,
    }
    return requisitos


@app.post("/recomendar", response_model=RespuestaRecomendacion)
def recomendar(entrada: ConsultaEstructuradaReq):
    req = requisitos_desde_consulta(entrada)
    top_k = req.get("cantidad_candidatos", 10) or 10

    conn = get_connection()
    candidatos_rows = get_all_candidates(conn)

    vectores = []
    rows_lista = []

    for row in candidatos_rows:
        feats = build_structured_features(req, row)
        vec = features_to_vector(feats, FEATURE_ORDER)
        vectores.append(vec)
        rows_lista.append(row)

    if not vectores:
        return RespuestaRecomendacion(consulta=req, candidatos=[])

    X = np.array(vectores, dtype=float)
    # Probabilidad de clase 1 (candidato idóneo)
    scores = MODEL.predict_proba(X)[:, 1]

    candidatos_con_score = []
    for row, score in zip(rows_lista, scores):
        candidatos_con_score.append((row, float(score)))

    # Ordenar de mayor a menor score
    candidatos_con_score.sort(key=lambda x: x[1], reverse=True)

    candidatos_resp: List[CandidatoResp] = []
    for row, score in candidatos_con_score[:top_k]:
        candidatos_resp.append(
            CandidatoResp(
                id=row["id"],
                nombre=row["nombre"],
                cargo=row["cargo"],
                habilidades=row["habilidades"],
                experiencia_anios=row["experiencia_anios"],
                idiomas=row["idiomas"] or "",
                ubicacion=row["ubicacion"] or "",
                modalidad=row["modalidad"] or "",
                disponibilidad=row["disponibilidad"] or "",
                score=round(score, 4),
            )
        )

    return RespuestaRecomendacion(
        consulta=req,
        candidatos=candidatos_resp,
    )
