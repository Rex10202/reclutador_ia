import os
import sqlite3
from typing import Any
import pandas as pd

from .config import BASE_DIR, DB_PATH, RAW_CSV_PATH
from .db import insert_candidate, get_connection

SCHEMA_PATH = os.path.join(BASE_DIR, "app", "schema.sql")


def crear_base_y_tabla() -> None:
    """
    Elimina la base de datos anterior (si existe) y crea una nueva tabla
    'candidatos' aplicando el esquema definido en schema.sql.
    """
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()
    print(f"[OK] Base y tabla creadas en {DB_PATH}")


def limpiar_ubicacion(loc: Any) -> str:
    """
    Limpia pequeñas inconsistencias en el campo de ubicación, por ejemplo
    comillas extra en valores como '"Cali"'.
    """
    if not isinstance(loc, str):
        return ""
    loc = loc.strip().strip('"').strip()
    return loc


def normalizar_idioma(lang: Any) -> str:
    """
    Normaliza valores de idioma a formas más legibles.
    """
    if not isinstance(lang, str):
        return ""
    l = lang.strip().lower()
    if "ingles" in l:
        return "Inglés"
    if "espanol" in l or "español" in l:
        return "Español"
    if "frances" in l or "francés" in l:
        return "Francés"
    if "portugues" in l or "portugués" in l:
        return "Portugués"
    return lang.strip()


def skills_semicolon_to_comma(skills: Any) -> str:
    """
    Convierte 'a;b;c' -> 'a, b, c' para almacenarlo de forma homogénea.
    """
    if not isinstance(skills, str):
        return ""
    parts = [p.strip() for p in skills.split(";") if p.strip()]
    return ", ".join(parts)


def cargar_candidatos_desde_csv() -> None:
    """
    Lee sample_queries.csv (alias RAW_CSV_PATH) y genera un candidato sintético
    por cada fila.
    """
    df = pd.read_csv(RAW_CSV_PATH)

    # Rellenar NaN y limpiar columnas clave
    for col in ["query_text", "role", "skills", "languages", "location"]:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str)

    if "experience_years" in df.columns:
        df["experience_years"] = df["experience_years"].fillna(0).astype(float)
    else:
        df["experience_years"] = 0.0

    conn = get_connection()

    for idx, row in df.iterrows():
        # Nombre sintético: usa id si existe, si no, índice+1
        if "id" in df.columns:
            try:
                nombre = f"Candidato {int(row['id'])}"
            except Exception:
                nombre = f"Candidato {idx+1}"
        else:
            nombre = f"Candidato {idx+1}"

        cargo = row.get("role", "")
        habilidades = skills_semicolon_to_comma(row.get("skills", ""))
        experiencia_anios = int(row.get("experience_years", 0.0) or 0.0)

        idioma_norm = normalizar_idioma(row.get("languages", ""))
        ubicacion = limpiar_ubicacion(row.get("location", ""))

        modalidad = "No especificada"
        disponibilidad = "Inmediata"
        descripcion = row.get("query_text", "")

        candidato = {
            "nombre": nombre,
            "cargo": cargo,
            "habilidades": habilidades,
            "experiencia_anios": experiencia_anios,
            "idiomas": idioma_norm,
            "nivel_idioma": "",
            "ubicacion": ubicacion,
            "modalidad": modalidad,
            "disponibilidad": disponibilidad,
            "descripcion": descripcion,
        }

        insert_candidate(conn, candidato)

    conn.close()
    print(f"[OK] {len(df)} candidatos sintéticos insertados en la BD.")


if __name__ == "__main__":
    crear_base_y_tabla()
    cargar_candidatos_desde_csv()
