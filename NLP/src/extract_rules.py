import re
from typing import Iterable, List, Optional

from spacy.tokens import Doc


NUM_CANDIDATES_PATTERN = re.compile(
	r"(?P<num>\d+)\s+(candidatos?|perfiles?|personas?|ingenieros?|t[eé]cnicos?)",
	flags=re.IGNORECASE,
)

YEARS_EXPERIENCE_PATTERN = re.compile(
	r"(?P<num>\d+)\s+años?\s+de\s+experiencia",
	flags=re.IGNORECASE,
)

# Expresiones alternativas: "mínimo 3 años", "al menos 5 años"
YEARS_EXPERIENCE_ALT_PATTERN = re.compile(
	r"(mínimo|al menos)\s+(?P<num>\d+)\s+años",
	flags=re.IGNORECASE,
)

# Expresiones negativas: "sin experiencia", "sin experiencia previa"
NO_EXPERIENCE_PATTERN = re.compile(
	r"sin\s+experiencia(\s+previa)?",
	flags=re.IGNORECASE,
)


def extract_num_candidates(text: str) -> Optional[int]:
	"""Extrae el número de candidatos solicitados si se menciona.

	Ejemplos: ``"3 candidatos"``, ``"2 perfiles"``.
	"""

	match = NUM_CANDIDATES_PATTERN.search(text)
	if not match:
		return None
	try:
		return int(match.group("num"))
	except ValueError:
		return None


def extract_experience(text: str) -> Optional[int]:
	"""Extrae años de experiencia a partir de expresiones simples.

	Ejemplo: ``"5 años de experiencia"``.
	"""

	# Caso explícito "sin experiencia"
	if NO_EXPERIENCE_PATTERN.search(text):
		return 0

	match = YEARS_EXPERIENCE_PATTERN.search(text)
	if not match:
		match = YEARS_EXPERIENCE_ALT_PATTERN.search(text)
	if not match:
		return None
	try:
		return int(match.group("num"))
	except ValueError:
		return None


def _strip_accents(text: str) -> str:
	"""Devuelve ``text`` sin tildes para comparaciones robustas."""

	replacements = str.maketrans("áéíóúÁÉÍÓÚ", "aeiouAEIOU")
	return text.translate(replacements)


def extract_location(doc: Doc, cities: Iterable[str]) -> Optional[str]:
	"""Devuelve la primera ciudad colombiana mencionada en el texto.

	Se compara contra un pequeño catálogo de ciudades, ignorando tildes.
	"""

	text_norm = _strip_accents(doc.text.lower())
	for city in cities:
		city_norm = _strip_accents(city.lower())
		if city_norm in text_norm:
			return city
	return None


def extract_languages(text: str, languages: Iterable[str]) -> List[str]:
	"""Devuelve los idiomas mencionados explícitamente en el texto.

	La comparación es insensible a mayúsculas y tildes ("ingles" vs
	"inglés").
	"""

	found: List[str] = []
	text_norm = _strip_accents(text.lower())
	for lang in languages:
		lang_norm = _strip_accents(lang.lower())
		if lang_norm in text_norm:
			found.append(lang)
	return found


__all__ = [
	"extract_num_candidates",
	"extract_experience",
	"extract_location",
	"extract_languages",
]

