import sqlite3
from typing import List, Dict, Any
from .config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def insert_candidate(conn, candidato: Dict[str, Any]):
    sql = """
    INSERT INTO candidatos (
        nombre, cargo, habilidades, experiencia_anios,
        idiomas, nivel_idioma, ubicacion, modalidad,
        disponibilidad, descripcion
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    conn.execute(sql, (
        candidato["nombre"],
        candidato["cargo"],
        candidato["habilidades"],
        candidato["experiencia_anios"],
        candidato.get("idiomas", ""),
        candidato.get("nivel_idioma", ""),
        candidato.get("ubicacion", ""),
        candidato.get("modalidad", ""),
        candidato.get("disponibilidad", ""),
        candidato.get("descripcion", ""),
    ))
    conn.commit()

def get_all_candidates(conn) -> List[sqlite3.Row]:
    cur = conn.execute("SELECT * FROM candidatos")
    return cur.fetchall()
