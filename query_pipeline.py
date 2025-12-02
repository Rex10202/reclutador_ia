# query_pipeline.py
from __future__ import annotations

from dataclasses import asdict
from typing import List, Tuple, Optional
import re

from NLP.src.parser import parse_query
from ranking_model.src.ranking_features import QueryRequirements as RankingQuery, run_ranking
from ranking_model.src.ranking_orchestrator import _normalize_text
from ranking_model.src.ranking_engine import get_all_roles, get_all_skills
from job_query_filter import analyze_job_query


# ----------------- Excepciones específicas -----------------


class NotAJobQuery(Exception):
    """El texto no parece una búsqueda de trabajo/candidatos."""


class NoCandidatesFound(Exception):
    """No hay candidatos que cumplan con lo pedido."""


# ----------------- Inferir cuántos candidatos quiere -----------------


def _infer_num_candidates(raw_text: str, nlp_num: Optional[int]) -> Optional[int]:
    """
    Regla:
      - Si NLP ya extrajo un número (ej. '3 candidatos') -> usar ese.
      - Si no, pero el texto suena a 'uno solo' (un/una/1) -> devolver 1.
      - En caso contrario -> None (el orquestador usará DEFAULT_TOP_N).
    """
    if nlp_num is not None and nlp_num > 0:
        return nlp_num

    text = (raw_text or "").lower()

    # Si menciona 'varios', 'algunos', 'muchos', NO limitar a 1.
    if any(w in text for w in ["varios", "algunos", "muchos"]):
        return None

    # '1 ingeniero', '1 técnico', etc.
    if re.search(r"\b1\s+\w+", text):
        return 1

    # 'necesito un ...', 'busco un ...', 'requiero un ...', 'solicito un ...'
    if re.search(r"\b(necesito|busco|requiero|solicito)\s+un[a]?\b", text):
        return 1

    return None


# ----------------- Inferir rol desde el catálogo -----------------


def _infer_role_from_catalog(raw_text: str, nlp_role: Optional[str]) -> Optional[str]:
    """
    Usa el texto completo + el catálogo de roles (candidates.csv) para
    decidir el rol más probable.

    - Si hay match claro con algún rol del catálogo (por tokens),
      se usa ese rol.
    - Si no, se hace fallback al rol que venga de NLP.
    """
    text_norm = _normalize_text(raw_text)
    q_tokens = set(text_norm.split())

    best_role: Optional[str] = None
    best_score: float = 0.0

    for role in get_all_roles():
        r_norm = _normalize_text(role)
        if not r_norm:
            continue
        r_tokens = set(r_norm.split())

        # intersección de tokens: 'analista de datos' vs 'una analista de datos'
        inter = q_tokens & r_tokens
        score = float(len(inter))

        # Bonus si el rol completo aparece dentro del texto
        if r_norm in text_norm or text_norm in r_norm:
            score += 0.5

        if score > best_score:
            best_score = score
            best_role = role

    # Si no encontramos nada razonable, usar lo que diga NLP (puede ser algo general)
    if best_role is None or best_score == 0.0:
        return nlp_role

    return best_role


# ----------------- Inferir skills desde el catálogo -----------------


def _infer_skills_from_catalog(
    raw_text: str,
    nlp_skills: Optional[List[str]],
) -> List[str]:
    """
    Combina:
      - skills estructuradas que haya detectado NLP (si las hay)
      - skills que realmente aparecen en el texto, usando el catálogo
        dinámico de skills que hay en candidates.csv

    Ej:
      texto: '... que sepa mantenimiento preventivo y correctivo, power bi y sql ...'
      -> ['mantenimiento preventivo', 'mantenimiento correctivo', 'power bi', 'sql']
    """
    result: List[str] = []
    seen = set()

    # 1) Skills que ya vengan de NLP
    if nlp_skills:
        for s in nlp_skills:
            s_clean = s.strip()
            if s_clean and s_clean not in seen:
                result.append(s_clean)
                seen.add(s_clean)

    # 2) Skills del catálogo que aparezcan en el texto
    text_norm = _normalize_text(raw_text)
    for skill in get_all_skills():
        sk_norm = _normalize_text(skill)
        if not sk_norm:
            continue
        if sk_norm in text_norm and skill not in seen:
            result.append(skill)
            seen.add(skill)

    return result


# ----------------- Pipeline principal -----------------


def run_query_pipeline(raw_text: str):
    """
    Orquesta todo:
      1) Filtro 'esto es una búsqueda de trabajo'
      2) NLP.parse_query (NO tocamos carpeta NLP)
      3) Inferir rol desde catálogo (roles en CSV) + NLP
      4) Inferir skills desde catálogo (skills en CSV) + NLP
      5) Inferir cuántos candidatos quiere
      6) Llamar a ranking_model.run_ranking
    """
    text = (raw_text or "").strip()
    if not text:
        raise ValueError("La consulta no puede estar vacía.")

    # 1) Filtro ligero de 'texto de trabajo'
    is_job, score = analyze_job_query(text)
    print(f"=== JOB_FILTER score={score:.3f} is_job={is_job} ===")
    if not is_job:
        raise NotAJobQuery("Tu solicitud no corresponde al objetivo de esta app (búsqueda de candidatos).")

    # 2) NLP: parseo estructurado
    print("\n=== NLP INPUT ===")
    print("raw_text:", repr(text))
    nlp_q = parse_query(text)

    print("=== NLP OUTPUT (NLP.QueryRequirements) ===")
    role_text = getattr(nlp_q, "role_text", None)
    print("role_text:", role_text)
    print("skills:", getattr(nlp_q, "skills", None))
    print("location:", getattr(nlp_q, "location", None))
    print("years_experience:", getattr(nlp_q, "years_experience", None))
    print("num_candidates:", getattr(nlp_q, "num_candidates", None))
    print("languages:", getattr(nlp_q, "languages", None))

    # 3) Rol: usar catálogo + NLP
    nlp_role = role_text or getattr(nlp_q, "role", None)
    ranking_role = _infer_role_from_catalog(text, nlp_role)

    # 4) Skills: catálogo + NLP + texto completo como contexto
    inferred_skills = _infer_skills_from_catalog(text, getattr(nlp_q, "skills", None))
    skills_for_ranking: List[str] = list(inferred_skills)
    # Añadimos el texto completo como 'contexto' adicional para el embedding
    skills_for_ranking.append(text)

    # 5) Ubicación, años, idiomas
    location_req = getattr(nlp_q, "location", None)
    years_req = getattr(nlp_q, "years_experience", None)
    langs = getattr(nlp_q, "languages", None) or []

    # 6) ¿cuántos candidatos quiere?
    nlp_num = getattr(nlp_q, "num_candidates", None)
    num_req = _infer_num_candidates(text, nlp_num)

    # 7) Construir query para el ranking semántico/orquestador
    ranking_q = RankingQuery(
        role=ranking_role,
        skills=skills_for_ranking,
        location=location_req,
        years_exp=years_req,
        languages=langs,
        num_candidates=num_req,
    )

    ranked_candidates, used_query = run_ranking(ranking_q)

    print("=== RANKING OUTPUT (top candidates) ===")
    print(f"count: {len(ranked_candidates)}")
    for c in ranked_candidates:
        print(c.id, c.role, "score:", c.score)

    if not ranked_candidates:
        raise NoCandidatesFound("No hay candidatos que cumplan con lo solicitado en este momento.")

    return ranked_candidates, used_query
