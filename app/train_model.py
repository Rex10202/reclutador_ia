from typing import List, Dict, Any
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

from .db import get_all_candidates, get_connection
from .features import build_structured_features, features_to_vector
from .config import MODEL_PATH, SAMPLE_QUERIES_PATH


def normalizar_texto_simple(s: Any) -> str:
    if not isinstance(s, str):
        return ""
    s = s.strip()
    s = s.replace('"', "")
    return s


def cargar_consultas_desde_csv() -> pd.DataFrame:
    df = pd.read_csv(SAMPLE_QUERIES_PATH)

    # Limpiar strings básicos de las columnas estructuradas
    for col in ["role", "skills", "languages", "location"]:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).apply(normalizar_texto_simple)

    # Años de experiencia
    if "experience_years" in df.columns:
        df["experience_years"] = df["experience_years"].fillna(0).astype(float)
    else:
        df["experience_years"] = 0.0

    # Número de candidatos solicitados
    if "num_candidates" in df.columns:
        df["num_candidates"] = df["num_candidates"].fillna(10).astype(int)
    else:
        df["num_candidates"] = 10

    return df


def parse_skills(skills_str: str) -> List[str]:
    if not isinstance(skills_str, str):
        return []
    return [s.strip() for s in skills_str.split(";") if s.strip()]


def parse_idiomas(lang_str: str) -> List[str]:

    if not isinstance(lang_str, str) or not lang_str.strip():
        return []

    lang = lang_str.strip().lower()
    if "ingles" in lang:
        return ["Inglés"]
    if "espanol" in lang or "español" in lang:
        return ["Español"]
    if "frances" in lang or "francés" in lang:
        return ["Francés"]
    if "portugues" in lang or "portugués" in lang:
        return ["Portugués"]

    # Si no coincide con nada, lo dejamos literal
    return [lang_str.strip()]


def requisitos_desde_fila_csv(row) -> Dict[str, Any]:
    cargo = row.get("role", "")
    skills_list = parse_skills(row.get("skills", ""))
    idiomas_list = parse_idiomas(row.get("languages", ""))
    exp_years = row.get("experience_years", 0.0) or 0.0
    ubicacion = row.get("location", "")
    num_cand = int(row.get("num_candidates", 10) or 10)

    req = {
        "cargo": cargo,
        "habilidades": skills_list,
        "idiomas": idiomas_list,
        "experiencia_minima": int(exp_years),
        "ubicacion": ubicacion,
        "modalidad": "",  # el CSV no incluye modalidad explícita
        "cantidad_candidatos": num_cand,
    }
    return req


def etiqueta_por_reglas(requisitos: Dict[str, Any], candidato_row) -> int:
    cargo_req = (requisitos.get("cargo", "") or "").lower()
    cargo_cand = (candidato_row["cargo"] or "").lower()

    if cargo_req and cargo_req not in cargo_cand:
        return 0

    hab_req = [h.lower() for h in requisitos.get("habilidades", [])]
    hab_cand = [h.strip().lower() for h in (candidato_row["habilidades"] or "").split(",") if h.strip()]
    if hab_req and not (set(hab_req) & set(hab_cand)):
        return 0

    exp_req = requisitos.get("experiencia_minima", 0) or 0
    exp_cand = candidato_row["experiencia_anios"] or 0
    if exp_req > 0 and exp_cand < exp_req:
        return 0

    return 1


def main() -> None:
    # 1) Cargar candidatos desde la BD
    conn = get_connection()
    candidatos = get_all_candidates(conn)
    print(f"[INFO] Candidatos cargados desde la BD: {len(candidatos)}")

    # 2) Cargar consultas estructuradas desde sample_queries.csv
    df_q = cargar_consultas_desde_csv()
    print(f"[INFO] Consultas en sample_queries.csv: {len(df_q)}")

    # Orden de las características
    feature_order = [
        "cargo_match",
        "habilidades_jaccard",
        "habilidades_match_count",
        "experiencia_candidato",
        "experiencia_minima",
        "experiencia_suficiente",
        "experiencia_delta",
        "idiomas_jaccard",
        "ubicacion_match",
        "modalidad_match",
    ]

    X = []
    y = []

    # 3) Generar dataset de entrenamiento: pares (consulta estructurada, candidato)
    for _, row in df_q.iterrows():
        req = requisitos_desde_fila_csv(row)
        for cand in candidatos:
            feats = build_structured_features(req, cand)
            vec = features_to_vector(feats, feature_order)
            label = etiqueta_por_reglas(req, cand)
            X.append(vec)
            y.append(label)

    X_arr = np.array(X, dtype=float)
    y_arr = np.array(y, dtype=int)

    if len(set(y_arr)) < 2:
        print("[ADVERTENCIA] Las reglas generaron solo una clase (todo 0 o todo 1).")
        print("Ajusta las reglas o agrega más consultas/candidatos.")
        return

    X_train, X_test, y_train, y_test = train_test_split(
        X_arr, y_arr, test_size=0.3, random_state=42, stratify=y_arr
    )

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("[INFO] Reporte de clasificación:")
    print(classification_report(y_test, y_pred))

    # 4) Guardar modelo
    bundle = {
        "model": model,
        "feature_order": feature_order,
    }
    joblib.dump(bundle, MODEL_PATH)
    print(f"[OK] Modelo guardado en {MODEL_PATH}")


if __name__ == "__main__":
    main()
