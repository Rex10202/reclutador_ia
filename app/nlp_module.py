import re
from typing import List, Dict, Any

CARGOS_CONOCIDOS = [
    "desarrollador backend",
    "desarrollador frontend",
    "analista de datos",
    "diseñador ux",
    "ingeniero de datos",
]

HABILIDADES_CONOCIDAS = [
    "python", "django", "flask", "fastapi",
    "sql", "postgresql", "mysql",
    "power bi", "excel",
    "figma", "react", "vue",
]

CIUDADES = [
    "bogotá", "medellín", "barranquilla", "cartagena", "cali"
]

MODALIDADES = ["remoto", "presencial", "híbrido", "hibrido"]

IDIOMAS = ["inglés", "ingles", "español", "espanol", "francés", "frances", "portugués", "portugues"]

def normalizar(texto: str) -> str:
    texto = texto.lower()
    texto = texto.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    texto = re.sub(r"[^a-z0-9ñ\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto

def extraer_cargo(texto_norm: str) -> str:
    for cargo in CARGOS_CONOCIDOS:
        c_norm = normalizar(cargo)
        if c_norm in texto_norm:
            return cargo
    return ""

def extraer_habilidades(texto_norm: str) -> List[str]:
    habilidades = []
    for hab in HABILIDADES_CONOCIDAS:
        h_norm = normalizar(hab)
        if re.search(r"\b" + re.escape(h_norm) + r"\b", texto_norm):
            habilidades.append(hab)
    return habilidades

def extraer_ubicacion(texto_norm: str) -> str:
    for ciudad in CIUDADES:
        c_norm = normalizar(ciudad)
        if re.search(r"\b" + re.escape(c_norm) + r"\b", texto_norm):
            return ciudad
    # Palabras claves remotas tipo "remoto" no son ubicación, pero sí modalidad
    return ""

def extraer_modalidad(texto_norm: str) -> str:
    for mod in MODALIDADES:
        m_norm = normalizar(mod)
        if re.search(r"\b" + re.escape(m_norm) + r"\b", texto_norm):
            return mod
    return ""

def extraer_idiomas(texto_norm: str) -> List[str]:
    encontrados = []
    for idioma in IDIOMAS:
        i_norm = normalizar(idioma)
        if re.search(r"\b" + re.escape(i_norm) + r"\b", texto_norm):
            # Normalizamos la forma al nombre “bonito”
            if "ingles" in i_norm:
                encontrados.append("Inglés")
            elif "espanol" in i_norm:
                encontrados.append("Español")
            elif "frances" in i_norm:
                encontrados.append("Francés")
            elif "portugues" in i_norm:
                encontrados.append("Portugués")
    return list(set(encontrados))

def extraer_experiencia(texto_norm: str) -> int:
    """
    Busca patrones como '3 anos', '3 años', '3 de experiencia'.
    Como ya normalizamos tildes, trabajamos con 'anos' y 'ano'.
    """
    m = re.search(r"(\d+)\s+(anos|ano|años|ano de experiencia|anos de experiencia)", texto_norm)
    if m:
        return int(m.group(1))
    return 0

def extraer_cantidad_candidatos(texto_norm: str) -> int:
    """
    Ejemplo: 'muéstrame 5 candidatos', 'busco 3 personas'.
    """
    m = re.search(r"(\d+)\s+(candidatos|personas|perfiles)", texto_norm)
    if m:
        return int(m.group(1))
    return 10  # valor por defecto

def interpretar_consulta(texto: str) -> Dict[str, Any]:
    texto_norm = normalizar(texto)

    cargo = extraer_cargo(texto_norm)
    habilidades = extraer_habilidades(texto_norm)
    ubicacion = extraer_ubicacion(texto_norm)
    modalidad = extraer_modalidad(texto_norm)
    idiomas = extraer_idiomas(texto_norm)
    experiencia = extraer_experiencia(texto_norm)
    cantidad = extraer_cantidad_candidatos(texto_norm)

    requisitos = {
        "texto_original": texto,
        "texto_normalizado": texto_norm,
        "cargo": cargo,
        "habilidades": habilidades,
        "ubicacion": ubicacion,
        "modalidad": modalidad,
        "idiomas": idiomas,
        "experiencia_minima": experiencia,
        "cantidad_candidatos": cantidad,
    }
    return requisitos

if __name__ == "__main__":
    ejemplo = "Busco un desarrollador backend con Python y Django, remoto, en Bogotá, con al menos 3 años de experiencia y que hable inglés. Muéstrame 5 candidatos."
    print(interpretar_consulta(ejemplo))
