from __future__ import annotations

import unicodedata
from dataclasses import asdict
from typing import List, Optional, Tuple, Dict, Any

from .config import DEFAULT_TOP_N
from .ranking_engine import (
    SemanticRankingEngine,
    RankingQueryRequirements,
    RankedCandidate,
)


# --------- Utilidades de normalización ---------


def _normalize_text(text: str) -> str:
    """
    Minúsculas y sin tildes para comparaciones robustas.
    """
    if not text:
        return ""
    text = text.lower()
    text = "".join(
        c
        for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )
    return text.strip()


def _split_role_tokens(role: str) -> List[str]:
    return [tok for tok in _normalize_text(role).split() if tok]


def _is_general_role(role_text: str) -> Tuple[bool, Optional[str]]:
    """
    Decide si un rol es general (1 token) o específico (>1 token).
    Devuelve (is_general, head_word)
    """
    toks = _split_role_tokens(role_text)
    if not toks:
        return True, None
    if len(toks) == 1:
        return True, toks[0]
    return False, toks[0]


# --------- Filtros deterministas ---------


def _filter_by_role(
    candidates: List[RankedCandidate],
    role_text: Optional[str],
) -> List[RankedCandidate]:
    """
    Filtro léxico por rol. SOLO se fija en el texto del rol,
    no en embeddings. La parte semántica ya se hizo antes.

    Importante: si no encuentra nada, devuelve [] y la capa superior
    decide si hace fallback al ranking puramente semántico o no.
    """
    if not role_text:
        return candidates

    is_general, head = _is_general_role(role_text)
    if head is None:
        return candidates

    role_norm = _normalize_text(role_text)

    def match_general(c: RankedCandidate) -> bool:
        # Ej: "ingeniero" -> cualquier rol que contenga token 'ingeniero'
        return head in _split_role_tokens(c.role)

    def match_specific(c: RankedCandidate) -> bool:
        # Ej: "ingeniero de mantenimiento" contenido en el rol normalizado
        return role_norm in _normalize_text(c.role)

    # Caso general: "ingeniero", "tecnico", "programador", etc.
    if is_general:
        general_matches = [c for c in candidates if match_general(c)]
        return general_matches

    # Caso específico: "ingeniero de mantenimiento", "analista de datos"
    specific_matches = [c for c in candidates if match_specific(c)]
    if specific_matches:
        return specific_matches

    # Fallback: si no hay match específico, intentar al menos por la palabra cabeza
    general_matches = [c for c in candidates if match_general(c)]
    return general_matches


def _filter_by_location(
    candidates: List[RankedCandidate],
    location: Optional[str],
) -> List[RankedCandidate]:
    if not location:
        return candidates

    loc_norm = _normalize_text(location)

    def match(c: RankedCandidate) -> bool:
        return _normalize_text(c.location) == loc_norm

    return [c for c in candidates if match(c)]


def _filter_by_years_experience(
    candidates: List[RankedCandidate],
    min_years: Optional[int],
) -> List[RankedCandidate]:
    if min_years is None:
        return candidates
    return [c for c in candidates if c.years_experience >= min_years]


# --------- API pública del orquestador ---------


class RankingOrchestrator:
    """
    Punto de entrada para la capa de aplicación.
    Lógica:
      - llama al motor semántico
      - aplica filtros deterministas
      - corta al top_n

    Mejora clave:
      - Si el filtro por rol deja 0 candidatos, miramos el score semántico.
        * Si el mejor score es ALTO -> usamos el ranking semántico tal cual
          (sin filtro de rol), útil para sinónimos / abreviaciones:
             "analizador de datos" -> "analista de datos"
             "programador"         -> "desarrollador backend/frontend"
        * Si el mejor score es BAJO -> devolvemos 0 candidatos
          (casos como "peluquero" cuando no hay nada parecido).
    """

    def __init__(self) -> None:
        self._engine = SemanticRankingEngine()

    def run_ranking(
        self,
        req: RankingQueryRequirements,
        num_candidates: Optional[int] = None,
    ) -> List[RankedCandidate]:
        """
        Ejecuta ranking completo:
          - ranking semántico (embeddings)
          - filtro por rol general/específico (léxico)
          - filtro por ubicación
          - filtro por años de experiencia
          - limitación a N resultados
        """
        # 0) Ranking semántico base
        all_ranked = self._engine.run_ranking(req)
        if not all_ranked:
            return []

        # 1) Filtro por rol (léxico)
        filtered = _filter_by_role(all_ranked, req.role)

        # --- Fallback semántico cuando el filtro léxico mata todo ---
        if not filtered:
            best_score = all_ranked[0].score
            print(
                f"[INFO] Sin match léxico para rol {req.role!r}. "
                f"Mejor score semántico: {best_score:.3f}"
            )

            # Umbral mínimo para considerar que el modelo encontró algo razonable
            SEMANTIC_MIN_FOR_FALLBACK = 0.40

            if best_score >= SEMANTIC_MIN_FOR_FALLBACK:
                # Devolvemos el ranking semántico completo sin filtrar por rol,
                # para permitir sinónimos y abreviaciones.
                print(
                    "[INFO] Usando fallback semántico: se ignora filtro por rol "
                    "y se usan los candidatos ordenados solo por embeddings."
                )
                filtered = all_ranked.copy()
            else:
                # No hay nada semánticamente cercano: no sugerimos nada.
                print(
                    "[INFO] Score semántico insuficiente; no hay candidatos "
                    "relacionados con el rol solicitado."
                )
                return []

        # 2) Filtro por ubicación
        filtered = _filter_by_location(filtered, req.location)

        # 3) Filtro por años de experiencia
        filtered = _filter_by_years_experience(filtered, req.years_experience)

        if not filtered:
            return []

        # 4) Limitación
        top_n = num_candidates if num_candidates is not None else DEFAULT_TOP_N
        return filtered[:top_n]

    # Helper opcional para devolver dicts listos para JSON
    def run_ranking_as_dicts(
        self,
        req: RankingQueryRequirements,
        num_candidates: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        ranked = self.run_ranking(req, num_candidates=num_candidates)
        # Redondeo de score
        result = []
        for c in ranked:
            d = asdict(c)
            d["score"] = round(c.score, 3)
            result.append(d)
        return result
