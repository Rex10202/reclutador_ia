from pathlib import Path
from typing import List
import uvicorn

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from query_pipeline import run_query_pipeline, NotAJobQuery, NoCandidatesFound


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


# ---------- Esquemas API ----------

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


# ---------- Endpoint principal ----------

@app.post("/query", response_model=FullResponse)
def handle_query(payload: QueryRequest):
    text = (payload.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="El texto de la consulta no puede estar vacío.")

    try:
        ranked_candidates, used_query = run_query_pipeline(text)
    except NotAJobQuery as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NoCandidatesFound as e:
        raise HTTPException(status_code=404, detail=str(e))

    # used_query es RankingQuery (el de ranking_model/src/ranking_features.py)
    parsed_resp = ParsedQueryResponse(
        role=used_query.role,
        skills=used_query.skills or [],
        location=used_query.location,
        years_experience=used_query.years_exp,
        num_candidates=used_query.num_candidates,
        languages=used_query.languages or [],
    )

    def _join(items: List[str]) -> str:
        return ";".join(items) if items else ""

    candidate_items = [
        CandidateResponse(
            id=c.id,
            role=c.role,
            skills=_join(c.skills),
            location=c.location,
            years_experience=int(c.years_experience),
            languages=_join(c.languages),
            score=float(c.score),
        )
        for c in ranked_candidates
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
