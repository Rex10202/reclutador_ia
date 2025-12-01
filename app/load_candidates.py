import os
import sqlite3
from typing import Any
import pandas as pd
from .config import BASE_DIR, DB_PATH, RAW_CSV_PATH
from .db import insert_candidate, get_connection

SCHEMA_PATH = os.path.join(BASE_DIR, "app", "schema.sql")


def crear_base_y_tabla() -> None:
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()
    print(f"[OK] Base y tabla creadas en {DB_PATH}")


def limpiar_str(x: Any) -> str:
    if not isinstance(x, str):
        return ""
    return x.strip().strip('"').strip()


def cargar_candidatos_desde_csv() -> None:
    if not os.path.exists(RAW_CSV_PATH):
        raise FileNotFoundError(
            f"No se encontró el archivo de candidatos: {RAW_CSV_PATH}\n"
            "Crea data/candidatos_reales.csv con tus candidatos reales."
        )

    df = pd.read_csv(RAW_CSV_PATH)

    columnas_esperadas = [
        "id",
        "nombre",
        "cargo",
        "habilidades",
        "experiencia_anios",
        "idiomas",
        "nivel_idioma",
        "ubicacion",
        "modalidad",
        "disponibilidad",
        "descripcion",
    ]

    for col in columnas_esperadas:
        if col not in df.columns:
            if col == "experiencia_anios":
                df[col] = 0
            else:
                df[col] = ""

    for col in [
        "nombre",
        "cargo",
        "habilidades",
        "idiomas",
        "nivel_idioma",
        "ubicacion",
        "modalidad",
        "disponibilidad",
        "descripcion",
    ]:
        df[col] = df[col].fillna("").apply(limpiar_str)

    # Experiencia a entero
    df["experiencia_anios"] = df["experiencia_anios"].fillna(0).astype(int)

    conn = get_connection()

    for _, row in df.iterrows():
        candidato = {
            "nombre": row["nombre"],
            "cargo": row["cargo"],
            "habilidades": row["habilidades"],  
            "experiencia_anios": int(row["experiencia_anios"]),
            "idiomas": row["idiomas"],          
            "nivel_idioma": row["nivel_idioma"],
            "ubicacion": row["ubicacion"],
            "modalidad": row["modalidad"],
            "disponibilidad": row["disponibilidad"],
            "descripcion": row["descripcion"],
        }
        insert_candidate(conn, candidato)

    conn.close()
    print(f"[OK] {len(df)} candidatos reales insertados en la BD.")


if __name__ == "__main__":
    crear_base_y_tabla()
    cargar_candidatos_desde_csv()
