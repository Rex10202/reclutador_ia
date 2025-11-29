#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fase 4: Integración en aplicación web (FastAPI).

- Endpoint POST /recomendar
- Recibe una consulta en lenguaje natural.
- Interpreta la consulta (Fase 2).
- Construye features con los candidatos (Fase 3).
- Usa modelo entrenado para puntuar afinidad y devuelve top-k.
"""

from typing import List, Dict, Any
import joblib
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel

from .config import MODEL_PATH
from .db import get_connection, get_all_candidates
from .nlp_module import interpretar_consulta
from .features import build_structured_features, features_to_vector

app = FastAPI(
    title="Recomendador de Candidatos para Talento Humano",
    description="Herramienta web basada en IA y NLP para recomendar candidatos.",
    version="0.1.0",
)

# Cargamos modelo al iniciar
_model_bundle = joblib.load(MODEL_PATH)
MODEL = _model_bundle["model"]
FEATURE_ORDER = _model_bundle["feature_order"]

class ConsultaReq(BaseModel):
    consulta: str

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
    descripcion: str
    score: float

class RespuestaRecomendacion(BaseModel):
    consulta: str
    requisitos: Dict[str, Any]
    candidatos: List[CandidatoResp]

@app.post("/recomendar", response_model=RespuestaRecomendacion)
def recomendar(entrada: ConsultaReq):
    req = interpretar_consulta(entrada.consulta)
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
        return RespuestaRecomendacion(
            consulta=entrada.consulta,
            requisitos=req,
            candidatos=[],
        )

    X = np.array(vectores)
    # Probabilidad de clase 1 (candidato idóneo)
    scores = MODEL.predict_proba(X)[:, 1]

    candidatos_con_score = []
    for row, score in zip(rows_lista, scores):
        candidatos_con_score.append((row, float(score)))

    # Ordenar de mayor a menor score
    candidatos_con_score.sort(key=lambda x: x[1], reverse=True)

    # Construir respuesta top_k
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
                descripcion=row["descripcion"] or "",
                score=round(score, 4),
            )
        )

    return RespuestaRecomendacion(
        consulta=entrada.consulta,
        requisitos=req,
        candidatos=candidatos_resp,
    )
