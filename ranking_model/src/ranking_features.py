from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from .ranking_engine import RankingQueryRequirements, RankedCandidate
from .ranking_orchestrator import RankingOrchestrator, _normalize_text


__all__ = [
    "QueryRequirements",
    "run_ranking",
    "build_candidate_features",
    "score_candidate",
]


# --------------------------------------------------------------------------------------
# API PRINCIPAL PARA app.py
# --------------------------------------------------------------------------------------


@dataclass
class QueryRequirements:
    """
    Clase de alto nivel que usa la app (FastAPI).
    """
    role: Optional[str] = None
    skills: Optional[List[str]] = None
    location: Optional[str] = None
    years_exp: Optional[int] = None
    languages: Optional[List[str]] = None
    num_candidates: Optional[int] = None

    def to_ranking_requirements(self) -> RankingQueryRequirements:
        """
        Convierte a la estructura interna que usa el motor semántico.
        """
        return RankingQueryRequirements(
            role=self.role,
            skills=self.skills,
            location=self.location,
            years_experience=self.years_exp,
            languages=self.languages,
        )


_orchestrator: Optional[RankingOrchestrator] = None


def _get_orchestrator() -> RankingOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = RankingOrchestrator()
    return _orchestrator


def run_ranking(query_req: QueryRequirements) -> Tuple[list[RankedCandidate], QueryRequirements]:
    """
    Función de alto nivel pensada para ser llamada desde app.py.

    Devuelve:
      - lista de RankedCandidate ya ordenados y filtrados
      - el mismo QueryRequirements para logging/debug
    """
    orchestrator = _get_orchestrator()
    internal_req = query_req.to_ranking_requirements()

    ranked = orchestrator.run_ranking(
        internal_req,
        num_candidates=query_req.num_candidates,
    )
    return ranked, query_req


# --------------------------------------------------------------------------------------
# MODELO CLÁSICO (EXPERIMENTAL, NO USADO EN PRODUCCIÓN)
# --------------------------------------------------------------------------------------


@dataclass
class CandidateFeatures:
    role_match: float
    skills_match: float
    location_match: float
    experience_score: float
    language_score: float
    candidate_id: str


def _to_norm_set(items: List[str]) -> set:
    return {_normalize_text(x) for x in items if _normalize_text(x)}


def build_candidate_features(
    candidate: RankedCandidate,
    req: QueryRequirements,
) -> CandidateFeatures:
    # Rol
    role_match = 0.0
    if req.role:
        r_q = _normalize_text(req.role)
        r_c = _normalize_text(candidate.role)
        if r_q and r_q in r_c:
            role_match = 1.0

    # Skills
    skills_match = 0.0
    if req.skills:
        cand_skills = _to_norm_set(candidate.skills)
        req_terms = _to_norm_set(req.skills)
        if cand_skills and req_terms:
            inter = cand_skills & req_terms
            skills_match = len(inter) / len(req_terms)

    # Location
    location_match = 0.0
    if req.location:
        if _normalize_text(candidate.location) == _normalize_text(req.location):
            location_match = 1.0

    # Experiencia
    experience_score = 0.0
    if req.years_exp is not None:
        diff = candidate.years_experience - req.years_exp
        experience_score = 1.0 if diff >= 0 else 0.0

    # Idiomas
    language_score = 0.0
    if req.languages:
        cand_lang = _to_norm_set(candidate.languages)
        req_lang = _to_norm_set(req.languages)
        if cand_lang and req_lang:
            inter = cand_lang & req_lang
            language_score = len(inter) / len(req_lang)

    return CandidateFeatures(
        role_match=role_match,
        skills_match=skills_match,
        location_match=location_match,
        experience_score=experience_score,
        language_score=language_score,
        candidate_id=candidate.id,
    )


def score_candidate(features: CandidateFeatures) -> float:
    w_role = 0.3
    w_skills = 0.3
    w_location = 0.2
    w_experience = 0.1
    w_language = 0.1

    s = (
        w_role * features.role_match
        + w_skills * features.skills_match
        + w_location * features.location_match
        + w_experience * features.experience_score
        + w_language * features.language_score
    )
    return float(s)

