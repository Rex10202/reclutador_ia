import json
from pathlib import Path
from typing import Dict, List, Optional

from .schema import QueryRequirements
from .spacy_utils import get_doc, iter_noun_chunks
from .beto_utils import precompute_catalog_embeddings, most_similar
from .extract_rules import (
	extract_experience,
	extract_languages,
	extract_location,
	extract_num_candidates,
)

CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"


def _load_json_list(path: Path) -> List[str]:
	with path.open("r", encoding="utf-8") as f:
		return json.load(f)


_ROLES = _load_json_list(CONFIG_DIR / "roles.json")
_SKILLS = _load_json_list(CONFIG_DIR / "skills.json")
_CITIES = _load_json_list(CONFIG_DIR / "cities_co.json")
_LANGUAGES = _load_json_list(CONFIG_DIR / "languages.json")

_ROLE_EMBEDS: Dict[str, object] = precompute_catalog_embeddings(_ROLES)
_SKILL_EMBEDS: Dict[str, object] = precompute_catalog_embeddings(_SKILLS)


def _detect_role(doc_text: str, noun_chunks: List[str]) -> Optional[str]:
	"""Detecta el rol principal usando spans nominales + BETO.

	Para la PoC priorizamos chunks que contengan palabras como
	"ingeniero" o "técnico" y luego aplicamos similitud semántica
	contra el catálogo de roles.
	"""

	candidate_spans: List[str] = []
	lowered = doc_text.lower()
	trigger_words = ("ingeniero", "técnico", "jefe")

	for chunk in noun_chunks:
		if any(tw in chunk.lower() for tw in trigger_words):
			candidate_spans.append(chunk)

	# Si no encontramos nada, usamos todo el texto como fallback.
	if not candidate_spans:
		candidate_spans.append(doc_text)

	best_role: Optional[str] = None
	best_score: float = 0.0
	for span in candidate_spans:
		for label, score in most_similar(span, _ROLE_EMBEDS, top_k=3):
			if score > best_score:
				best_role, best_score = label, score

	# Umbral simple para evitar asignaciones muy forzadas.
	if best_score < 0.5:
		return None
	return best_role


def _strip_accents(text: str) -> str:
	"""Devuelve ``text`` sin tildes para comparaciones de skills."""

	replacements = str.maketrans("áéíóúÁÉÍÓÚ", "aeiouAEIOU")
	return text.translate(replacements)


def _detect_skills(text: str, noun_chunks: List[str]) -> List[str]:
	"""Detecta skills mencionadas en el texto.

	Estrategia para la PoC de ingeniero de mantenimiento:
	- Coincidencia literal de cada skill del catálogo.
	- Regla especial para "mantenimiento preventivo y correctivo".
	- No se añaden sugerencias semánticas automáticas; priorizamos
	  únicamente lo que el usuario menciona de forma explícita.
	"""

	found: List[str] = []
	# Normalizamos a minúsculas y sin tildes para ser más robustos a
	# variaciones de escritura ("mecánica" vs "mecanica").
	lowered = _strip_accents(text.lower())

	# Regla especial: "mantenimiento preventivo y correctivo"
	if "mantenimiento preventivo" in lowered and "correctivo" in lowered:
		for target in ("mantenimiento preventivo", "mantenimiento correctivo"):
			if target in _SKILLS and target not in found:
				found.append(target)

	# Coincidencias literales generales
	for skill in _SKILLS:
		skill_lower = _strip_accents(skill.lower())
		if skill_lower in lowered and skill not in found:
			found.append(skill)

	return found


def parse_query(text: str) -> QueryRequirements:
	"""Parsea una consulta en lenguaje natural y devuelve requisitos.

	Esta primera versión está centrada en el caso "ingeniero de
	mantenimiento" y usos cercanos.
	"""

	if not text or not text.strip():
		raise ValueError("La consulta no puede estar vacía.")

	doc = get_doc(text)

	noun_chunks = list(iter_noun_chunks(doc))
	role = _detect_role(doc.text, noun_chunks)

	skills = _detect_skills(doc.text, noun_chunks)
	years_experience = extract_experience(doc.text)
	num_candidates = extract_num_candidates(doc.text)
	location = extract_location(doc, _CITIES)
	languages = extract_languages(doc.text, _LANGUAGES)

	return QueryRequirements(
		role=role,
		skills=skills,
		location=location,
		years_experience=years_experience,
		num_candidates=num_candidates,
		languages=languages,
	)


__all__ = ["parse_query"]

