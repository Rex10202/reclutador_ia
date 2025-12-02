# query_adapter.py
from __future__ import annotations

from typing import Any, List, Optional, Tuple
import re

from ranking_model.src.ranking_features import QueryRequirements


# ----------------- Heurística para extraer el rol desde el texto crudo -----------------


def _infer_role_fallback(text: str) -> Optional[str]:
    """
    Intenta inferir el nombre del cargo a partir del texto libre,
    sin tocar la lógica de NLP.

    Ejemplos manejados:
      - 'necesito un ingeniero de mantenimiento'
      - 'solicito ingeniero de sistemas'
      - 'requiero 2 técnicos electricistas'
      - 'busco un piloto comercial'

    No usa lista de cargos, sólo verbos 'de intención' y limpieza básica.
    """

    if not text:
        return None

    # Quitar espacios y signos de puntuación finales
    clean = text.strip()
    clean = re.sub(r"[.!?…]+$", "", clean).strip()

    lower = clean.lower()

    # Verbos/frases "de intención" típicas al pedir personal
    intent_pattern = re.compile(
        r"""
        ^(
            necesito|
            busco|
            requiero|
            solicito|
            quiero|
            deseo|
            contrato|
            contratar|
            estoy\s+buscando|
            estamos\s+buscando|
            se\s+necesita|
            se\s+requiere|
            se\s+busca
        )\s+(?P<rest>.+)$
        """,
        flags=re.IGNORECASE | re.VERBOSE,
    )

    m = intent_pattern.match(lower)
    if m:
        rest = m.group("rest").strip()
    else:
        # Si no detectamos verbo de intención, usamos el texto tal cual
        rest = lower

    # Quitar número al inicio (ej. '1 ingeniero de mantenimiento')
    rest = re.sub(r"^\d+\s+", "", rest).strip()

    tokens = rest.split()
    if not tokens:
        return None

    # Determinantes comunes (no es lista de cargos, es muy pequeña)
    determiners = {"un", "una", "el", "la", "los", "las", "unos", "unas"}
    if tokens[0] in determiners and len(tokens) >= 2:
        tokens = tokens[1:]

    if not tokens:
        return None

    # Limitamos longitud para evitar frases kilométricas:
    # 'ingeniero', 'ingeniero de mantenimiento', 'ingeniero en sistemas', etc.
    if len(tokens) > 8:
        return None

    role = " ".join(tokens).strip()
    if not role:
        return None

    # Normalización ligera: 'ingenieria' -> 'ingeniero' cuando aplica
    toks = role.split()
    if toks and toks[0].startswith("ingenieria"):
        if len(toks) == 1:
            role = "ingeniero"
        else:
            role = "ingeniero " + " ".join(toks[1:])

    return role or None


# ----------------- Adaptador NLP -> QueryRequirements del ranking -----------------


def adapt_nlp_to_ranking(
    raw_text: str,
    nlp_q: Any,
) -> Tuple[QueryRequirements, dict, bool]:
    """
    Pega lo que sale del parser NLP con lo que necesita el motor de ranking.

    Devuelve:
      - QueryRequirements (el que usa ranking_model.src.ranking_features)
      - un dict 'parsed' para llenar ParsedQueryResponse en la API
      - un bool 'looks_like_job' que indica si el texto parece una solicitud de candidato
    """

    # Extraemos campos del dataclass de NLP de forma segura
    role_text = getattr(nlp_q, "role_text", None)
    is_general = getattr(nlp_q, "is_general", False)  # por si quieres loguearlo
    head_word = getattr(nlp_q, "head_word", None)
    skills = getattr(nlp_q, "skills", None) or []
    location = getattr(nlp_q, "location", None)
    years_experience = getattr(nlp_q, "years_experience", None)
    num_candidates = getattr(nlp_q, "num_candidates", None)
    languages = getattr(nlp_q, "languages", None) or []

    # 1) Determinar rol que usará el ranking
    role_for_ranking: Optional[str] = role_text

    # Si NLP no encontró rol, usamos la heurística de fallback
    if not role_for_ranking:
        role_for_ranking = _infer_role_fallback(raw_text)
        if role_for_ranking:
            print(f"[INFO] Fallback de rol aplicado: {role_for_ranking!r}")

    # 2) Construir 'skills' para el modelo semántico
    #    (texto completo + skills estructuradas que haya detectado NLP)
    skills_for_ranking: List[str] = []
    if raw_text:
        skills_for_ranking.append(raw_text)
    if skills:
        skills_for_ranking.extend(skills)

    # 3) Construir objeto de alto nivel que entiende ranking_model
    ranking_req = QueryRequirements(
        role=role_for_ranking,
        skills=skills_for_ranking or None,
        location=location,
        years_exp=years_experience,
        languages=languages or None,
        num_candidates=num_candidates,
    )

    # 4) Heurística sencilla para decidir si esto parece una búsqueda de candidato
    looks_like_job = bool(
        role_for_ranking
        or years_experience is not None
        or location
        or skills
        or languages
        or num_candidates is not None
    )

    # 5) Dict para ParsedQueryResponse (lo que ve el frontend)
    parsed = {
        "role": role_for_ranking,
        "skills": skills,
        "location": location,
        "years_experience": years_experience,
        "num_candidates": num_candidates,
        "languages": languages,
    }

    return ranking_req, parsed, looks_like_job
