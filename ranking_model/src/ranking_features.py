from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional


@dataclass
class QueryRequirements:
	"""Esquema mínimo usado por ranking_model para no depender de NLP.

	Mantiene los mismos nombres de campos para que la API pueda
	madear fácilmente desde el objeto que venga del módulo NLP.
	"""

	role: Optional[str] = None
	skills: List[str] = field(default_factory=list)
	location: Optional[str] = None
	years_experience: Optional[int] = None
	num_candidates: Optional[int] = None
	languages: List[str] = field(default_factory=list)


def _split_semicolon_list(value: str) -> List[str]:
	if not value:
		return []
	return [item.strip() for item in value.split(";") if item.strip()]


def build_candidate_features(
	query: QueryRequirements,
	candidate: Dict[str, str],
) -> Dict[str, float]:
	"""Construye un conjunto de *features* numéricas consulta–candidato.

	Todas las salidas son escala 0–1 o valores numéricos sencillos para
	un primer modelo interpretable de ranking.
	"""

	q = asdict(query)
	q_role = (q.get("role") or "").lower()
	q_skills: List[str] = [s.lower() for s in q.get("skills") or []]
	q_location = (q.get("location") or "").lower()
	q_years = q.get("years_experience")
	q_langs: List[str] = [l.lower() for l in q.get("languages") or []]

	c_role = (candidate.get("role") or "").lower()
	c_skills = [s.lower() for s in _split_semicolon_list(candidate.get("skills", ""))]
	c_location = (candidate.get("location") or "").lower()
	try:
		c_years = int(candidate.get("years_experience") or 0)
	except ValueError:
		c_years = 0
	c_langs = [l.lower() for l in _split_semicolon_list(candidate.get("languages", ""))]

	# 1) Coincidencia de rol (0–1)
	role_match = 0.0
	if q_role and c_role:
		if q_role == c_role:
			role_match = 1.0
		elif q_role in c_role or c_role in q_role:
			role_match = 0.7

	# 2) Skills: proporción de skills requeridas presentes en el candidato
	if q_skills:
		common_skills = set(q_skills).intersection(c_skills)
		skills_match = len(common_skills) / len(set(q_skills))
	else:
		skills_match = 0.0

	# 3) Ubicación: 1 si misma ciudad, 0.5 si ciudad vacía en query,
	# 0 en otro caso.
	if q_location and c_location:
		location_match = 1.0 if q_location == c_location else 0.0
	elif not q_location:
		location_match = 0.5
	else:
		location_match = 0.0

	# 4) Experiencia: 1 si cumple o supera; lineal decreciente si se
	# queda corto, 0 si no se especifica.
	raw_years_gap = 0.0
	if q_years is not None:
		if c_years >= q_years:
			experience_score = 1.0
			# diferencia absoluta de años por encima del mínimo requerido
			raw_years_gap = float(c_years - q_years)
		else:
			gap = q_years - c_years
			# penalización simple: pierde 0.2 por año de gap, mínimo 0
			experience_score = max(0.0, 1.0 - 0.2 * gap)
	else:
		experience_score = 0.5

	# 5) Idiomas: 1 si todos los idiomas requeridos están presentes.
	if q_langs:
		lang_ok = all(lang in c_langs for lang in q_langs)
		language_score = 1.0 if lang_ok else 0.0
	else:
		language_score = 0.5

	return {
		"role_match": role_match,
		"skills_match": skills_match,
		"location_match": location_match,
		"experience_score": experience_score,
		"language_score": language_score,
		"raw_years_gap": raw_years_gap,
	}


__all__ = ["build_candidate_features"]

