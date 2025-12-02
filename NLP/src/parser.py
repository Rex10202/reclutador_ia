<<<<<<< HEAD
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
=======
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from difflib import SequenceMatcher
import json
import re

from sentence_transformers import SentenceTransformer


# ----------------- Embeddings para ranking -----------------

_st_model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Devuelve embeddings para una lista de textos usando sentence-transformers.
    """
    return _st_model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=False,
    ).tolist()


# ----------------- Carga de catálogos -----------------
>>>>>>> ade873c (Flexibilidad agente)

CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"


def _load_json_list(path: Path) -> List[str]:
<<<<<<< HEAD
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

=======
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


# Catálogo de roles, por ejemplo:
# ["ingeniero civil", "ingeniero de mantenimiento", "analista de datos",
#  "técnico electricista", "peluquero canino", "piloto comercial", ...]
_ROLES = _load_json_list(CONFIG_DIR / "roles.json")


# ----------------- Utilidades de texto -----------------

def _strip_accents(text: str) -> str:
    return text.translate(str.maketrans("áéíóúÁÉÍÓÚñÑ", "aeiouAEIOUnN"))


def _normalize(text: str) -> str:
    """
    Normaliza el texto:
    - pasa a minúsculas
    - quita acentos
    - elimina signos raros
    - colapsa espacios
    """
    t = _strip_accents(text.lower())
    t = re.sub(r"[^\w\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(
        None,
        _strip_accents(a.lower()),
        _strip_accents(b.lower()),
    ).ratio()


def _trim_role_phrase(phrase: str) -> str:
    """
    Recorta la frase del rol para quitar cola de contexto:

      'ingeniero civil en cartagena'       -> 'ingeniero civil'
      'practicante de ingenieria civil para planta' -> 'practicante de ingenieria civil'

    Mantiene 'de' (ingeniero de mantenimiento), pero corta en 'en', 'para', 'con'.
    """
    if not phrase:
        return phrase

    tokens = phrase.split()
    stop_tokens = {"en", "para", "con"}

    result = []
    for tok in tokens:
        if tok in stop_tokens and result:
            break
        result.append(tok)

    return " ".join(result).strip()


def _extract_role_text(norm: str) -> Optional[str]:
    """
    Intenta extraer el 'nombre de trabajo' del texto.
    Ejemplos:
      'un ingeniero civil en cartagena'     -> 'ingeniero civil'
      'busco un ingeniero'                 -> 'ingeniero'
      'ingeniero de sistemas en bogota'    -> 'ingeniero de sistemas'
      'ingenieria civil'                   -> 'ingenieria civil'
    """
    # Caso 1: hay determinante (un/una/el/la)
    m = re.search(r"\b(un|una|el|la)\s+(.+)$", norm)
    if m:
        role_txt = m.group(2).strip()
        role_txt = _trim_role_phrase(role_txt)
        return role_txt or None

    # Caso 2: todo el texto es el rol (ej. 'ingeniero', 'ingeniero civil', 'ingenieria civil')
    role_txt = _trim_role_phrase(norm)
    return role_txt or None


def _match_catalog_role(role_text: str, roles: List[str], threshold: float = 0.9) -> Optional[str]:
    """
    Busca en el catálogo un rol casi idéntico al texto.
    Umbral alto (0.9) para NO relajar demasiado:
      'ingeniero civil' -> 'ingeniero civil' (OK)
      pero NO 'ingeniero civil' -> 'ingeniero de mantenimiento'
    """
    best = None
    best_s = 0.0
    for r in roles:
        s = _similarity(role_text, r)
        if s > best_s:
            best_s = s
            best = r
    return best if best_s >= threshold else None


# ----------------- Modelo de salida -----------------

@dataclass
class QueryRequirements:
    # Rol tal como lo escribió el usuario (ej. 'ingeniero', 'ingeniero civil', 'peluquero canino')
    role_text: Optional[str] = None
    # Rol del catálogo, solo si coincide casi exactamente (caso específico)
    role_catalog: Optional[str] = None
    # True si el usuario pidió algo general (una sola palabra: 'ingeniero', 'tecnico', 'peluquero')
    is_general: bool = False
    # Primera palabra del rol ('ingeniero', 'tecnico', 'peluquero', etc.)
    head_word: Optional[str] = None

    # Campos extendibles para el futuro (por ahora vacíos)
    skills: List[str] = None
    location: Optional[str] = None
    years_experience: Optional[int] = None
    num_candidates: Optional[int] = None
    languages: List[str] = None


# ----------------- Parser principal -----------------

def parse_query(text: str) -> QueryRequirements:
    if not text or not text.strip():
        raise ValueError("La consulta no puede estar vacía.")

    norm = _normalize(text)

    role_text = _extract_role_text(norm)
    role_catalog: Optional[str] = None
    is_general = False
    head_word: Optional[str] = None

    if role_text:
        tokens = role_text.split()

        # ----------------------------------------------------
        # NORMALIZACIONES ESPECIALES
        # 1) "ingenieria" (solo) -> "ingeniero" (general)
        # 2) "ingenieria X"     -> "ingeniero X" (específico)
        # ----------------------------------------------------
        if tokens and tokens[0] == "ingenieria":
            if len(tokens) == 1:
                # 'ingenieria' -> 'ingeniero' (caso general)
                role_text = "ingeniero"
                tokens = ["ingeniero"]
            else:
                # 'ingenieria civil' -> 'ingeniero civil'
                role_text = "ingeniero " + " ".join(tokens[1:])
                tokens = role_text.split()
        # ----------------------------------------------------

        head_word = tokens[0] if tokens else None

        # General si solo hay una palabra (ej. 'ingeniero', 'tecnico', 'peluquero', 'piloto')
        is_general = len(tokens) == 1

        # Solo intentamos mapear a catálogo cuando NO es general (específico)
        # Ej: 'ingeniero civil', 'tecnico electricista', 'peluquero canino'
        if not is_general:
            role_catalog = _match_catalog_role(role_text, _ROLES, threshold=0.9)

    return QueryRequirements(
        role_text=role_text,
        role_catalog=role_catalog,
        is_general=is_general,
        head_word=head_word,
        skills=[],
        location=None,
        years_experience=None,
        num_candidates=None,
        languages=[],
    )


__all__ = ["parse_query", "get_embeddings", "QueryRequirements"]
>>>>>>> ade873c (Flexibilidad agente)
