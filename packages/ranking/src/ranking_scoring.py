from __future__ import annotations

from typing import List, Tuple

from .ranking_engine import RankingQueryRequirements, RankedCandidate
from .ranking_features import build_candidate_features, CandidateFeatures


def score_candidate(features: CandidateFeatures) -> float:
    """
    Score lineal simple sobre las features.
    Este modelo es sólo experimental y no se usa en producción,
    dado que preferimos el modelo semántico de embeddings.
    """
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


def rerank_with_classic_model(
    candidates: List[RankedCandidate],
    req: RankingQueryRequirements,
) -> List[Tuple[RankedCandidate, float]]:
    """
    Opcional: dado un ranking semántico, reordena o inspecciona candidatos usando
    el modelo clásico de features. Devuelve (candidato, score_clásico).
    """
    results: List[Tuple[RankedCandidate, float]] = []
    for c in candidates:
        feats = build_candidate_features(c, req)
        s = score_candidate(feats)
        results.append((c, s))

    # Ordena de mayor a menor score clásico
    results.sort(key=lambda t: -t[1])
    return results

