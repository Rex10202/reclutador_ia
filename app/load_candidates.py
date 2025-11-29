#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fase 1: Construcción de la base de candidatos a partir de sample_queries.csv.

- Crea la base de datos SQLite.
- Ejecuta el esquema SQL (schema.sql).
- Lee sample_queries.csv.
- Transforma cada fila en un "perfil de candidato" sintético.
- Inserta los candidatos en la tabla 'candidatos'.

sample_queries.csv tiene columnas:
id, query_text, role, skills, languages, experience_years, location, num_candidates
"""

import os
import sqlite3
import pandas as pd

from .config import BASE_DIR, DB_PATH, RAW_CSV_PATH
from .db import insert_candidate

SCHEMA_PATH = os.path.join(BASE_DIR, "app", "schema.sql")


def crear_base_y_tabla():
    # Elimina la BD anterior si existe (para pruebas)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()
    print(f"[OK] Base y tabla creadas en {DB_PATH}")


def limpiar_ubicacion(loc):
    if not isinstance(loc, str):
        return ""
    # Quita espacios extras y comillas tipo "Cali"
    loc = loc.strip().strip('"').strip()
    return loc


def normalizar_idioma(lang):
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


def skills_semicolon_to_comma(skills):
    """
    Convierte: "mantenimiento preventivo;SAP PM"
    a:        "mantenimiento preventivo, SAP PM"
    """
    if not isinstance(skills, str):
        return ""
    parts = [p.strip() for p in skills.split(";") if p.strip()]
    return ", ".join(parts)


def cargar_candidatos_desde_csv():
    from .db import get_connection

    # RAW_CSV_PATH ahora es sample_queries.csv
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
        # Generamos un nombre sintético de candidato
        # por ejemplo: "Candidato 1", "Candidato 2", ...
        nombre = f"Candidato {int(row['id'])}" if "id" in df.columns else f"Candidato {idx+1}"

        cargo = row.get("role", "")
        habilidades = skills_semicolon_to_comma(row.get("skills", ""))
        experiencia_anios = int(row.get("experience_years", 0.0) or 0.0)

        idioma_norm = normalizar_idioma(row.get("languages", ""))
        ubicacion = limpiar_ubicacion(row.get("location", ""))

        # Modalidad y disponibilidad no vienen en el CSV, ponemos valores por defecto
        modalidad = "No especificada"
        disponibilidad = "Inmediata"

        descripcion = row.get("query_text", "")

        candidato = {
            "nombre": nombre,
            "cargo": cargo,
            "habilidades": habilidades,
            "experiencia_anios": experiencia_anios,
            "idiomas": idioma_norm,      # guardamos como string (ej: "Inglés")
            "nivel_idioma": "",          # vacio por ahora
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
