from pathlib import Path
<<<<<<< HEAD
from typing import List
import uvicorn

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from NLP.src.parser import parse_query
=======
from typing import List, Optional
import re
import unicodedata

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from NLP.src.parser import parse_query
from NLP.src.job_detector import es_trabajo
from NLP.src.extract_rules import extract_num_candidates, extract_experience
>>>>>>> ade873c (Flexibilidad agente)
from ranking_model.src.ranking_features import QueryRequirements as RankingQueryRequirements
from ranking_model.src.ranking_orchestrator import run_ranking

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(title="Talento Humano - PoC", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
<<<<<<< HEAD
    allow_origins=["*"],  # PoC
=======
    allow_origins=["*"],
>>>>>>> ade873c (Flexibilidad agente)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD
# Servir archivos estáticos (JS, CSS)
app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static",
)


=======
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# ----------------- Utilidades de normalización -----------------

def _strip_accents(text: str) -> str:
    return "".join(
        c
        for c in unicodedata.normalize("NFD", text or "")
        if unicodedata.category(c) != "Mn"
    )


def _normalize_role(text: str) -> str:
    t = _strip_accents((text or "").lower())
    t = re.sub(r"[^\w\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


# Catálogo simple de ciudades usado en los candidatos
CITY_CATALOG = [
    "Cartagena",
    "Barranquilla",
    "Bogotá",
    "Bogota",
    "Medellín",
    "Medellin",
    "Cali",
    "Remoto",
]


def infer_location_from_text(text: str) -> Optional[str]:
    norm_text = _normalize_role(text)
    for city in CITY_CATALOG:
        if _normalize_role(city) in norm_text:
            norm_city = _normalize_role(city)
            if norm_city == "bogota":
                return "Bogotá"
            if norm_city == "medellin":
                return "Medellín"
            return city
    return None


def infer_num_candidates_from_text(text: str) -> Optional[int]:
    """
    1) Busca expresiones tipo '3 candidatos', '2 perfiles' (usa extract_rule).
    2) Si no encuentra, interpreta 'un/una ...' como 1.
    """
    n = extract_num_candidates(text)
    if n is not None:
        return n

    if re.search(r"\b(un|una)\s+\w+", text.lower()):
        return 1

    return None


# ----------------- Esquemas de API -----------------

>>>>>>> ade873c (Flexibilidad agente)
class QueryRequest(BaseModel):
    text: str


class ParsedQueryResponse(BaseModel):
    role: str | None
    skills: List[str]
    location: str | None
    years_experience: int | None
    num_candidates: int | None
    languages: List[str]


class CandidateResponse(BaseModel):
    id: str
    role: str
    skills: str
    location: str
    years_experience: int
    languages: str
    score: float


class FullResponse(BaseModel):
    parsed_query: ParsedQueryResponse
    candidates: List[CandidateResponse]


<<<<<<< HEAD
=======
# ----------------- Endpoint principal -----------------

>>>>>>> ade873c (Flexibilidad agente)
@app.post("/query", response_model=FullResponse)
def handle_query(payload: QueryRequest):
    text = (payload.text or "").strip()
    if not text:
<<<<<<< HEAD
        raise HTTPException(status_code=400, detail="El texto de la consulta no puede estar vacío.")

    # LOG: lo que llega a NLP
    print("\n=== NLP INPUT ===")
    print("raw_text:", repr(text))

    # 1) NLP: parsear la consulta en un objeto de dominio
    nlp_q = parse_query(text)

    # LOG: lo que sale de NLP
    print("=== NLP OUTPUT (QueryRequirements) ===")
    print("role:", nlp_q.role)
    print("skills:", nlp_q.skills)
    print("location:", nlp_q.location)
    print("years_experience:", nlp_q.years_experience)
    print("num_candidates:", nlp_q.num_candidates)
    print("languages:", nlp_q.languages)

    # 2) Mapear a esquema de ranking
    ranking_q = RankingQueryRequirements(
        role=nlp_q.role,
        skills=nlp_q.skills,
        location=nlp_q.location,
        years_experience=nlp_q.years_experience,
        num_candidates=nlp_q.num_candidates,
        languages=nlp_q.languages,
    )

    # LOG: lo que se envía al modelo de ranking
    print("=== RANKING INPUT (RankingQueryRequirements) ===")
    print(ranking_q)

    # 3) Ejecutar ranking
    ranked = run_ranking(ranking_q)

    # LOG: lo que devuelve el modelo de ranking
    print("=== RANKING OUTPUT (top candidates) ===")
    print(f"count: {len(ranked)}")
    for item in ranked:
        print(item["id"], item["role"], "score:", item["score"])

    # 4) Construir respuesta
    parsed_resp = ParsedQueryResponse(
        role=nlp_q.role,
        skills=nlp_q.skills,
        location=nlp_q.location,
        years_experience=nlp_q.years_experience,
        num_candidates=nlp_q.num_candidates,
        languages=nlp_q.languages,
    )

    candidate_items = [
        CandidateResponse(
            id=item["id"],
            role=item["role"],
            skills=item["skills"],
            location=item["location"],
            years_experience=int(item["years_experience"]),
            languages=item["languages"],
            score=float(item["score"]),
        )
        for item in ranked
    ]

    return FullResponse(parsed_query=parsed_resp, candidates=candidate_items)


@app.get("/", response_class=HTMLResponse)
def serve_index():
    """Devuelve el index.html del frontend."""
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=500, detail="No se encontró frontend/index.html")
    return index_path.read_text(encoding="utf-8")


if __name__ == "__main__":

    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
=======
        raise HTTPException(status_code=400, detail="El campo 'text' no puede estar vacío.")

    # 1) Filtro NLI: ahora más robusto
    if not es_trabajo(text):
        raise HTTPException(
            status_code=400,
            detail="Tu solicitud no corresponde al objetivo de esta app (búsqueda de candidatos).",
        )

    # 2) Parseo NLP: rol general / específico
    nlp_q = parse_query(text)
    role_text = nlp_q.role_text          # ej. 'tecnico de mantenimiento'
    is_general = nlp_q.is_general        # True para 'ingeniero', 'tecnico', etc.
    head_word = nlp_q.head_word          # 'ingeniero', 'tecnico', etc.

    # 3) Extraer info adicional de la consulta (reglas)
    num_candidates = infer_num_candidates_from_text(text)
    years_req = extract_experience(text)          # int o None
    location_req = infer_location_from_text(text) # ciudad o None

    # 4) Determinar texto que se usará como "rol" para el ranking
    if role_text:
        ranking_role = role_text
    elif head_word:
        ranking_role = head_word
    else:
        ranking_role = "candidato"

    # 5) Construir query de ranking
    #    Truco: metemos TODO el texto en 'skills' para que el embedding
    #    considere la frase completa (rol, ciudad, años, skills...).
    ranking_q = RankingQueryRequirements(
        role=ranking_role,
        skills=[text],
        location=location_req,
        years_experience=years_req,
        num_candidates=None,  # el límite lo aplicamos después
        languages=[],
    )

    # 6) Ejecutar ranking (ordenados por score, sin filtros ni límites)
    ranked = run_ranking(ranking_q)

    if not ranked:
        raise HTTPException(
            status_code=404,
            detail="No hay candidatos registrados en la base de datos.",
        )

    def norm(s: str) -> str:
        return _normalize_role(s)

    results = ranked

    # 7) Filtrado por rol (general / específico)
    if head_word:
        hw_norm = norm(head_word)

        # ----- CASO GENERAL: 'ingeniero', 'tecnico', 'piloto', etc. -----
        if is_general:
            general_filtered = [
                c for c in ranked
                if hw_norm and hw_norm in norm(c["role"])
            ]
            if general_filtered:
                results = general_filtered

        # ----- CASO ESPECÍFICO: 'tecnico de mantenimiento', etc. -----
        else:
            rt_norm = norm(role_text) if role_text else ""

            specific_filtered = [
                c for c in ranked
                if rt_norm and rt_norm in norm(c["role"])
            ]

            if specific_filtered:
                results = specific_filtered
            else:
                general_filtered = [
                    c for c in ranked
                    if hw_norm and hw_norm in norm(c["role"])
                ]
                if general_filtered:
                    results = general_filtered
                else:
                    results = ranked

    # 8) Filtros adicionales fuertes: ubicación y experiencia

    if location_req:
        loc_norm = norm(location_req)
        loc_filtered = [
            c for c in results
            if loc_norm == norm(c["location"])
        ]
        if loc_filtered:
            results = loc_filtered

    if years_req is not None:
        exp_filtered = [
            c for c in results
            if c["years_experience"] >= years_req
        ]
        if exp_filtered:
            results = exp_filtered

    if not results:
        raise HTTPException(
            status_code=404,
            detail="No hay candidatos que cumplan con lo solicitado en este momento.",
        )

    # 9) Aplicar límite: si dijiste "un técnico" o "3 candidatos", respetamos eso
    if num_candidates and num_candidates > 0:
        results = results[:num_candidates]
    else:
        TOP_N = 50
        results = results[:TOP_N]

    candidates = [
        CandidateResponse(
            id=c["id"],
            role=c["role"],
            skills=c["skills"],
            location=c["location"],
            years_experience=c["years_experience"],
            languages=c["languages"],
            score=round(float(c["score"]), 6),
        )
        for c in results
    ]

    parsed_resp = ParsedQueryResponse(
        role=ranking_role,
        skills=[text],
        location=location_req,
        years_experience=years_req,
        num_candidates=num_candidates,
        languages=[],
    )

    return FullResponse(parsed_query=parsed_resp, candidates=candidates)


# ----------------- Servir frontend -----------------

@app.get("/", response_class=HTMLResponse)
def serve_index():
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="index.html no encontrado en frontend/")
    return index_path.read_text(encoding="utf-8")
>>>>>>> ade873c (Flexibilidad agente)
