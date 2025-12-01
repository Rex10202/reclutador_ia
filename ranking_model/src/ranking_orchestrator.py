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
