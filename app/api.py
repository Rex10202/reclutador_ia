from typing import List, Dict, Any, Optional
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

from .db import get_connection, get_all_candidates

# ------------------------------
# Carga del modelo de embeddings
# ------------------------------

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
EMBEDDING_MODEL = SentenceTransformer(MODEL_NAME)


# -----------------------------------
# Definición de la aplicación FastAPI
# -----------------------------------

app = FastAPI(
    title="Talento humano IA",
    description=(
        "Herramienta web basada en un modelo preentrenado multilingüe "
        "que calcula la afinidad entre una vacante"
        " y los perfiles de candidatos almacenados en la base de datos."
    ),
    version="0.3.0",
)

# -----------------------------------
# Esquemas de entrada/salida (Pydantic)
# -----------------------------------

class ConsultaEstructuradaReq(BaseModel):
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

# -----------------------------------
# Funciones auxiliares para texto
# -----------------------------------
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
        "cantidad_candidatos": num_cand,
    }
    return requisitos

def construir_texto_vacante(requisitos: Dict[str, Any]) -> str:
    partes = []

    cargo = requisitos.get("cargo", "").strip()
    if cargo:
        partes.append(f"Vacante para el cargo de {cargo}.")

    habilidades = requisitos.get("habilidades", [])
    if habilidades:
        partes.append("Se requieren habilidades en: " + ", ".join(habilidades) + ".")

    exp = requisitos.get("experiencia_minima", 0)
    if exp and exp > 0:
        partes.append(f"Se requiere al menos {exp} años de experiencia.")

    idiomas = requisitos.get("idiomas", [])
    if idiomas:
        partes.append("Idiomas requeridos: " + ", ".join(idiomas) + ".")

    ubicacion = requisitos.get("ubicacion", "").strip()
    if ubicacion:
        partes.append(f"Ubicación de la vacante: {ubicacion}.")

    if not partes:
        partes.append("Vacante sin requisitos específicos definidos.")

    return " ".join(partes)


def construir_texto_candidato(row) -> str:
    partes = []

    cargo = (row["cargo"] or "").strip()
    if cargo:
        partes.append(f"Cargo: {cargo}.")

    habilidades = (row["habilidades"] or "").strip()
    if habilidades:
        partes.append(f"Habilidades: {habilidades}.")

    exp = row["experiencia_anios"] or 0
    partes.append(f"Experiencia: {exp} años.")

    idiomas = (row["idiomas"] or "").strip()
    if idiomas:
        partes.append(f"Idiomas: {idiomas}.")

    ubicacion = (row["ubicacion"] or "").strip()
    if ubicacion:
        partes.append(f"Ubicación: {ubicacion}.")

    modalidad = (row["modalidad"] or "").strip()
    if modalidad:
        partes.append(f"Modalidad: {modalidad}.")

    disponibilidad = (row["disponibilidad"] or "").strip()
    if disponibilidad:
        partes.append(f"Disponibilidad: {disponibilidad}.")

    if not partes:
        partes.append("Perfil de candidato sin información detallada.")

    return " ".join(partes)


# -----------------------------------
# Carga inicial de candidatos + embeddings
# -----------------------------------

_conn_init = get_connection()
CANDIDATE_ROWS = get_all_candidates(_conn_init)
_conn_init.close()

CANDIDATE_TEXTS = [construir_texto_candidato(row) for row in CANDIDATE_ROWS]

CANDIDATE_EMBEDDINGS = EMBEDDING_MODEL.encode(
    CANDIDATE_TEXTS,
    convert_to_numpy=True,
    normalize_embeddings=True
)


# -----------------------------------
# Endpoint principal de recomendación
# -----------------------------------

@app.post("/recomendar", response_model=RespuestaRecomendacion)
def recomendar(entrada: ConsultaEstructuradaReq):
    requisitos = requisitos_desde_consulta(entrada)
    top_k = requisitos.get("cantidad_candidatos", 10) or 10

    texto_vacante = construir_texto_vacante(requisitos)

    query_emb = EMBEDDING_MODEL.encode(
        [texto_vacante],
        convert_to_numpy=True,
        normalize_embeddings=True
    )[0]

    scores = np.dot(CANDIDATE_EMBEDDINGS, query_emb)  # shape (num_candidatos,)

    candidatos_con_score = list(zip(CANDIDATE_ROWS, scores))
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
                score=round(float(score), 4),
            )
        )

    return RespuestaRecomendacion(
        consulta=requisitos,
        candidatos=candidatos_resp,
    )
