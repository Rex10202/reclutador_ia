from pathlib import Path
from typing import List
import uvicorn

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from NLP.src.parser import parse_query
from ranking_model.src.ranking_features import QueryRequirements as RankingQueryRequirements
from ranking_model.src.ranking_orchestrator import run_ranking

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(title="Talento Humano - PoC", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # PoC
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos (JS, CSS)
app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static",
)


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


@app.post("/query", response_model=FullResponse)
def handle_query(payload: QueryRequest):
    text = (payload.text or "").strip()
    if not text:
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