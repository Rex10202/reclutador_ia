#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Construcción de características (features) para el modelo de recomendación.
"""

from typing import Dict, Any, List
import math

def jaccard(list_a: List[str], list_b: List[str]) -> float:
    set_a = set([x.strip().lower() for x in list_a if x])
    set_b = set([x.strip().lower() for x in list_b if x])
    if not set_a and not set_b:
        return 0.0
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return inter / union if union > 0 else 0.0

def split_comma(text: str) -> List[str]:
    return [t.strip() for t in text.split(",") if t.strip()]

def build_structured_features(requisitos: Dict[str, Any], candidato_row) -> Dict[str, float]:
    """
    Genera características numéricas y booleanas entre la consulta y un candidato.
    """
    feats = {}

    # Cargo
    cargo_req = requisitos.get("cargo", "").lower()
    cargo_cand = (candidato_row["cargo"] or "").lower()
    feats["cargo_match"] = 1.0 if cargo_req and cargo_req in cargo_cand else 0.0

    # Habilidades
    hab_req = [h.lower() for h in requisitos.get("habilidades", [])]
    hab_cand = [h.lower() for h in split_comma(candidato_row["habilidades"] or "")]
    feats["habilidades_jaccard"] = jaccard(hab_req, hab_cand)
    feats["habilidades_match_count"] = float(len(set(hab_req) & set(hab_cand)))

    # Experiencia
    exp_req = requisitos.get("experiencia_minima", 0) or 0
    exp_cand = candidato_row["experiencia_anios"] or 0
    feats["experiencia_candidato"] = float(exp_cand)
    feats["experiencia_minima"] = float(exp_req)
    feats["experiencia_suficiente"] = 1.0 if exp_cand >= exp_req and exp_req > 0 else 0.0
    feats["experiencia_delta"] = float(exp_cand - exp_req)

    # Idiomas
    idiomas_req = [i.lower() for i in requisitos.get("idiomas", [])]
    idiomas_cand = [i.lower() for i in split_comma(candidato_row["idiomas"] or "")]
    feats["idiomas_jaccard"] = jaccard(idiomas_req, idiomas_cand)

    # Ubicación
    ub_req = (requisitos.get("ubicacion", "") or "").lower()
    ub_cand = (candidato_row["ubicacion"] or "").lower()
    feats["ubicacion_match"] = 1.0 if ub_req and ub_req in ub_cand else 0.0

    # Modalidad
    mod_req = (requisitos.get("modalidad", "") or "").lower()
    mod_cand = (candidato_row["modalidad"] or "").lower()
    feats["modalidad_match"] = 1.0 if mod_req and mod_req in mod_cand else 0.0

    return feats

def features_to_vector(feats: Dict[str, float], feature_order: List[str]) -> List[float]:
    return [float(feats.get(name, 0.0)) for name in feature_order]
