import csv
from pathlib import Path
from typing import Dict, List

from .ranking_features import QueryRequirements

from .ranking_features import build_candidate_features
from .ranking_scoring import score_candidate


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def load_candidates(path: Path | None = None) -> List[Dict[str, str]]:
	"""Carga la tabla de candidatos desde ``candidates.csv``."""

	if path is None:
		path = DATA_DIR / "candidates.csv"
	with path.open("r", encoding="utf-8") as f:
		reader = csv.DictReader(f)
		return list(reader)


def rank_candidates(
	query: QueryRequirements,
	candidates: List[Dict[str, str]] | None = None,
	limit: int | None = None,
) -> List[Dict[str, object]]:
	"""Devuelve la lista de candidatos ordenados por afinidad.

	Cada elemento de la lista contiene los campos originales del
	candidato más un campo adicional ``score`` con el puntaje calculado.
	"""

	if candidates is None:
		candidates = load_candidates()

	scored: List[Dict[str, object]] = []
	for cand in candidates:
		features = build_candidate_features(query, cand)
		score = score_candidate(features)
		item: Dict[str, object] = dict(cand)
		item["score"] = round(score, 4)
		scored.append(item)

	scored.sort(key=lambda x: x["score"], reverse=True)
	if limit is not None:
		return scored[:limit]
	return scored


__all__ = ["load_candidates", "rank_candidates"]

