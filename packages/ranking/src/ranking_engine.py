from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import csv
import os
from functools import lru_cache
import numpy as np

from .config import CANDIDATES_CSV_PATH
from .embeddings import get_embeddings, cosine_sim


# --------- Modelos de datos ---------


@dataclass
class RankingQueryRequirements:
    role: Optional[str] = None
    skills: Optional[List[str]] = None
    location: Optional[str] = None
    years_experience: Optional[int] = None
    languages: Optional[List[str]] = None


@dataclass
class RankedCandidate:
    id: str
    role: str
    skills: List[str]
    location: str
    years_experience: int
    languages: List[str]
    score: float
    raw_row: Dict[str, Any]


# --------- Utilidades ---------


def _safe_str(x: Any) -> str:
    if x is None:
        return ""
    if isinstance(x, float) and np.isnan(x):
        return ""
    return str(x)


def _load_candidates_raw() -> List[Dict[str, Any]]:
    """
    Lee candidates.csv a una lista de dicts sin usar pandas.
    Espera columnas:
      id, role, skills, location, years_experience, languages
    """
    path = str(CANDIDATES_CSV_PATH)
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el archivo de candidatos: {path}")

    rows: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        expected_cols = [
            "id",
            "role",
            "skills",
            "location",
            "years_experience",
            "languages",
        ]
        for col in expected_cols:
            if col not in reader.fieldnames:
                raise ValueError(f"Falta la columna '{col}' en {path}")

        for row in reader:
            rows.append(row)
    return rows


def _concat_candidate_text(row: Dict[str, Any]) -> str:
    role = _safe_str(row.get("role", ""))
    skills = _safe_str(row.get("skills", ""))
    location = _safe_str(row.get("location", ""))
    years_raw = row.get("years_experience", "0")
    try:
        years = int(years_raw)
    except Exception:
        years = 0
    languages = _safe_str(row.get("languages", ""))

    parts = [
        f"Rol: {role}",
        f"Skills: {skills}",
        f"Ubicación: {location}",
        f"Años de experiencia: {years}",
        f"Idiomas: {languages}",
    ]
    return " | ".join(parts)


def _build_query_text(req: RankingQueryRequirements) -> str:
    role = req.role or ""
    location = req.location or ""
    years = req.years_experience if req.years_experience is not None else ""
    skills = "; ".join(req.skills) if req.skills else ""
    languages = "; ".join(req.languages) if req.languages else ""

    parts = []
    if role:
        parts.append(f"Rol buscado: {role}")
    if skills:
        parts.append(f"Requisitos y descripción: {skills}")
    if location:
        parts.append(f"Ubicación deseada: {location}")
    if years != "":
        parts.append(f"Años de experiencia mínimos: {years}")
    if languages:
        parts.append(f"Idiomas requeridos: {languages}")

    if not parts:
        return "Búsqueda de candidato para un puesto."

    return " | ".join(parts)


# --------- Motor principal ---------


class SemanticRankingEngine:
    """
    Motor de ranking basado en embeddings semánticos.
    Carga y embebe a los candidatos al inicializar, para reutilizar en múltiples consultas.
    """

    def __init__(self) -> None:
        self._candidates_raw: List[Dict[str, Any]] = _load_candidates_raw()
        self._candidate_texts: List[str] = [
            _concat_candidate_text(row) for row in self._candidates_raw
        ]
        self._candidate_embeddings: np.ndarray = get_embeddings(self._candidate_texts)

    @property
    def candidates_raw(self) -> List[Dict[str, Any]]:
        return self._candidates_raw

    def run_ranking(self, req: RankingQueryRequirements) -> List[RankedCandidate]:
        """
        Devuelve todos los candidatos ordenados por similitud de coseno
        respecto al query construido desde RankingQueryRequirements.
        NO filtra por rol/ubicación/años; eso se deja a la capa superior.
        """
        query_text = _build_query_text(req)
        query_vec = get_embeddings([query_text])[0]  # (dim,)
        scores = cosine_sim(query_vec, self._candidate_embeddings)

        order = np.argsort(-scores)

        ranked: List[RankedCandidate] = []
        for idx in order:
            row = self._candidates_raw[int(idx)]
            score = float(scores[int(idx)])

            skills_list = [
                s.strip()
                for s in _safe_str(row.get("skills", "")).split(";")
                if s.strip()
            ]
            languages_list = [
                l.strip()
                for l in _safe_str(row.get("languages", "")).split(";")
                if l.strip()
            ]

            years_raw = row.get("years_experience", "0")
            try:
                years = int(years_raw)
            except Exception:
                years = 0

            ranked.append(
                RankedCandidate(
                    id=_safe_str(row.get("id", "")),
                    role=_safe_str(row.get("role", "")),
                    skills=skills_list,
                    location=_safe_str(row.get("location", "")),
                    years_experience=years,
                    languages=languages_list,
                    score=score,
                    raw_row=row,
                )
            )

        return ranked

@lru_cache(maxsize=1)
def get_all_roles() -> List[str]:
    """
    Devuelve la lista única de roles que existen en candidates.csv.
    Se usa como 'catálogo' dinámico de profesiones.
    """
    rows = _load_candidates_raw()
    roles: List[str] = []
    for r in rows:
        role = _safe_str(r.get("role", "")).strip()
        if role:
            roles.append(role)
    # sin duplicados
    return sorted(set(roles))


@lru_cache(maxsize=1)
def get_all_skills() -> List[str]:
    rows = _load_candidates_raw()
    skills_set: set[str] = set()
    for r in rows:
        raw = _safe_str(r.get("skills", ""))
        for s in raw.split(";"):
            s = s.strip()
            if s:
                skills_set.add(s)
    return sorted(skills_set)

