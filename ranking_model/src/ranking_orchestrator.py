<<<<<<< HEAD
from typing import Dict, List

from .ranking_engine import load_candidates, rank_candidates
from .ranking_features import QueryRequirements


def run_ranking(query: QueryRequirements) -> List[Dict[str, object]]:
    """Punto de entrada único del modelo de ranking."""
    limit = query.num_candidates or 5
    print("\n[ranking_model] run_ranking - query:", query)
    print("[ranking_model] limit:", limit)

    candidates = load_candidates()
    ranked = rank_candidates(query, candidates, limit=limit)
    print("[ranking_model] ranked count:", len(ranked))
    return ranked


__all__ = ["run_ranking"]
=======
from typing import Dict, List, Set
from pathlib import Path
import csv
import numpy as np

from .ranking_features import QueryRequirements
from NLP.src.parser import get_embeddings

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "candidates.csv"


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def load_candidates() -> List[Dict[str, object]]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"candidates.csv no encontrado en: {DATA_PATH}")

    rows: List[Dict[str, object]] = []
    with open(DATA_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(
                {
                    "id": r["id"],
                    "role": r["role"],
                    "skills": r["skills"],
                    "location": r["location"],
                    "years_experience": int(r["years_experience"]),
                    "languages": r["languages"],
                }
            )
    return rows


def available_roles() -> Set[str]:
    return {c["role"] for c in load_candidates()}


def _concat_fields(role, skills, location, years_experience, languages) -> str:
    skills_txt = skills if isinstance(skills, str) else ";".join(skills or [])
    langs_txt = languages if isinstance(languages, str) else ";".join(languages or [])
    return " ".join(
        filter(
            None,
            [
                role or "",
                skills_txt or "",
                location or "",
                str(years_experience or ""),
                langs_txt or "",
            ],
        )
    ).strip()


def run_ranking(q: QueryRequirements) -> List[Dict[str, object]]:
    """
    Calcula un score semántico consulta–candidato usando embeddings.
    NO filtra ni limita; devuelve todos los candidatos ordenados.
    """

    candidates = load_candidates()
    if not candidates:
        return []

    query_text = _concat_fields(
        q.role,
        q.skills,
        q.location,
        q.years_experience,
        q.languages,
    )

    candidate_texts = [
        _concat_fields(
            c["role"],
            c["skills"],
            c["location"],
            c["years_experience"],
            c["languages"],
        )
        for c in candidates
    ]

    embs = get_embeddings([query_text] + candidate_texts)
    q_emb = np.array(embs[0])
    cand_embs = [np.array(e) for e in embs[1:]]

    for cand, emb in zip(candidates, cand_embs):
        cand["score"] = _cosine(q_emb, emb)

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates


__all__ = ["run_ranking", "available_roles"]
>>>>>>> ade873c (Flexibilidad agente)
