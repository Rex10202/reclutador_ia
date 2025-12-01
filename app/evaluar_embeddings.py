
from typing import List, Set, Any
import numpy as np
import pandas as pd

from .api import (
    EMBEDDING_MODEL,
    CANDIDATE_ROWS,
    CANDIDATE_EMBEDDINGS,
    construir_texto_vacante,
    parse_skills,
    parse_idiomas,
)
from .config import EVAL_QUERIES_PATH


def precision_at_k(ranked_ids: List[int], relevant_ids: Set[int], k: int) -> float:
    if k <= 0:
        return 0.0
    top_k = ranked_ids[:k]
    if not top_k:
        return 0.0
    inter = len(set(top_k) & relevant_ids)
    return inter / float(k)


def recall_at_k(ranked_ids: List[int], relevant_ids: Set[int], k: int) -> float:
    if not relevant_ids:
        return 0.0
    top_k = ranked_ids[:k]
    inter = len(set(top_k) & relevant_ids)
    return inter / float(len(relevant_ids))


def hit_at_1(ranked_ids: List[int], relevant_ids: Set[int]) -> float:
    if not ranked_ids or not relevant_ids:
        return 0.0
    return 1.0 if ranked_ids[0] in relevant_ids else 0.0


def _safe_str(value: Any) -> str:

    if isinstance(value, str):
        return value.strip()
    return ""


def requisitos_desde_fila(row) -> dict:
    role = _safe_str(row.get("role", ""))
    skills_str = _safe_str(row.get("skills", ""))
    languages_str = _safe_str(row.get("languages", ""))
    exp_raw = row.get("experience_years", 0)

    try:
        exp = float(exp_raw or 0)
    except (TypeError, ValueError):
        exp = 0.0

    location = _safe_str(row.get("location", ""))
    num_cand_raw = row.get("num_candidates", 10)

    try:
        num_cand = int(num_cand_raw or 10)
    except (TypeError, ValueError):
        num_cand = 10

    habilidades = parse_skills(skills_str)
    idiomas = parse_idiomas(languages_str)

    req = {
        "cargo": role,
        "habilidades": habilidades,
        "idiomas": idiomas,
        "experiencia_minima": int(exp),
        "ubicacion": location,
        "cantidad_candidatos": num_cand,
    }
    return req


def main():
    df = pd.read_csv(EVAL_QUERIES_PATH)

    candidate_rows = CANDIDATE_ROWS
    candidate_embeddings = CANDIDATE_EMBEDDINGS

    print(f"[INFO] Consultas de evaluación: {len(df)}")
    print(f"[INFO] Candidatos en la base: {len(candidate_rows)}\n")

    # Acumuladores globales
    total_hit1 = 0.0
    total_p3 = 0.0
    total_r3 = 0.0
    total_p5 = 0.0
    total_r5 = 0.0
    n_queries = 0

    for _, row in df.iterrows():
        qid = row["id"]
        requisitos = requisitos_desde_fila(row)

        rel_str = _safe_str(row.get("relevant_ids", ""))
        if not rel_str:
            print(f"[ADVERTENCIA] Consulta {qid} no tiene relevant_ids definidos. Se omite.")
            continue

        relevant_ids: Set[int] = set()
        for tok in rel_str.split(";"):
            tok = tok.strip()
            if tok:
                try:
                    relevant_ids.add(int(tok))
                except ValueError:
                    pass

        if not relevant_ids:
            print(f"[ADVERTENCIA] Consulta {qid} no tiene IDs relevantes válidos. Se omite.")
            continue

        texto_vacante = construir_texto_vacante(requisitos)
        query_emb = EMBEDDING_MODEL.encode(
            [texto_vacante],
            convert_to_numpy=True,
            normalize_embeddings=True
        )[0]  # vector (d,)

        scores = np.dot(candidate_embeddings, query_emb)

        candidatos_con_score = list(zip(candidate_rows, scores))
        candidatos_con_score.sort(key=lambda x: x[1], reverse=True)
        ranked_ids = [row_cand["id"] for row_cand, _ in candidatos_con_score]

        h1 = hit_at_1(ranked_ids, relevant_ids)
        p3 = precision_at_k(ranked_ids, relevant_ids, 3)
        r3 = recall_at_k(ranked_ids, relevant_ids, 3)
        p5 = precision_at_k(ranked_ids, relevant_ids, 5)
        r5 = recall_at_k(ranked_ids, relevant_ids, 5)

        total_hit1 += h1
        total_p3 += p3
        total_r3 += r3
        total_p5 += p5
        total_r5 += r5
        n_queries += 1

        print(f"Consulta {qid}: {requisitos['cargo']} en {requisitos['ubicacion']}")
        print(f"  IDs relevantes: {sorted(relevant_ids)}")
        print(f"  Métricas:")
        print(f"    hit@1      = {h1:.3f}")
        print(f"    precision@3 = {p3:.3f}, recall@3 = {r3:.3f}")
        print(f"    precision@5 = {p5:.3f}, recall@5 = {r5:.3f}")
        print("-" * 60)

    if n_queries == 0:
        print("[ERROR] No se pudo evaluar ninguna consulta (n_queries=0). Revisa el CSV de evaluación.")
        return

    print("\n=== Métricas globales (promedio sobre todas las consultas) ===")
    print(f"Consultas evaluadas: {n_queries}")
    print(f"hit@1 promedio      = {total_hit1 / n_queries:.3f}")
    print(f"precision@3 promedio = {total_p3 / n_queries:.3f}")
    print(f"recall@3 promedio    = {total_r3 / n_queries:.3f}")
    print(f"precision@5 promedio = {total_p5 / n_queries:.3f}")
    print(f"recall@5 promedio    = {total_r5 / n_queries:.3f}")


if __name__ == "__main__":
    main()
