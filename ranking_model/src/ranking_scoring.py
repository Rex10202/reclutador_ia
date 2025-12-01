from typing import Dict


def score_candidate(features: Dict[str, float]) -> float:
	"""Combina features en un único puntaje de idoneidad.

	Primero usa una combinación lineal de las features principales y
	luego añade un pequeño término de desempate basado en experiencia.
	"""

	role_w = 0.25
	skills_w = 0.35
	exp_w = 0.25
	loc_w = 0.1
	lang_w = 0.05

	base = (
		role_w * features.get("role_match", 0.0)
		+ skills_w * features.get("skills_match", 0.0)
		+ exp_w * features.get("experience_score", 0.0)
		+ loc_w * features.get("location_match", 0.0)
		+ lang_w * features.get("language_score", 0.0)
	)

	# Término de desempate: si dos candidatos empatan en todo lo
	# anterior pero uno tiene mayor experiencia relativa, se le da
	# una ligera ventaja. Se espera que ``raw_years_gap`` sea la
	# diferencia (c_years - q_years) calculada en otro lugar; si no
	# está presente, se asume 0.
	raw_years_gap = features.get("raw_years_gap", 0.0)
	bonus = 0.001 * raw_years_gap

	return base + bonus


__all__ = ["score_candidate"]

