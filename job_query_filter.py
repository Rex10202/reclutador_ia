# job_query_filter.py
from __future__ import annotations

from typing import Tuple
import re


# ----------------- Patrones ligeros -----------------

# Verbos típicos de solicitar/contratar personas
_VERB_PATTERN = re.compile(
    r"\b(necesito|busco|requiero|solicito|contrato|contratar|se busca|se requiere|oferto|ofrecemos)\b",
    flags=re.IGNORECASE,
)

# Mención de años de experiencia
_EXPERIENCE_PATTERN = re.compile(
    r"\b\d+\s+años?\s+de\s+experiencia\b",
    flags=re.IGNORECASE,
)

# Pistas de "rol/trabajo" muy genéricas (stems, no lista gigante)
_ROLE_HINTS_PATTERN = re.compile(
    r"\b("
    r"ingenier\w*|t[eé]cnic\w*|analist\w*|desarrollador\w*|programador\w*|"
    r"contador\w*|abogad\w*|m[eé]dic\w*|enfermer\w*|diseñador\w*|"
    r"operari\w*|jefe|coordinador\w*|auxiliar\w*"
    r")\b",
    flags=re.IGNORECASE,
)


def analyze_job_query(text: str, threshold: float = 0.4) -> Tuple[bool, float]:
    """
    Analiza si un texto tiene pinta de ser una búsqueda de trabajo/candidato.

    No depende de NLP ni de modelos pesados.
    Devuelve:
      is_job: bool
      score: float en [0, 1] (solo una heurística)
    """
    clean = (text or "").strip()
    if not clean:
        return False, 0.0

    score = 0.0

    # 1) Verbo de solicitud ("necesito", "busco", "solicito", etc.)
    if _VERB_PATTERN.search(clean):
        score += 0.5

    # 2) Años de experiencia
    if _EXPERIENCE_PATTERN.search(clean):
        score += 0.3

    # 3) Pistas de rol/profesión
    if _ROLE_HINTS_PATTERN.search(clean):
        score += 0.4

    # Normalizar a [0, 1]
    if score > 1.0:
        score = 1.0

    is_job = score >= threshold
    return is_job, float(score)
