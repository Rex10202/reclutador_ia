from src.parser import parse_query


def test_parse_basic_ingeniero_mantenimiento():
    text = "Necesito un ingeniero de mantenimiento industrial con 5 años de experiencia en Bogotá, 3 candidatos con inglés."
    result = parse_query(text)

    assert result.role is not None
    assert "ingeniero de mantenimiento" in result.role.lower()
    assert result.years_experience == 5
    assert result.num_candidates == 3
    assert result.location == "Bogotá"
    assert any("inglés" in lang.lower() for lang in result.languages)


def test_parse_ingeniero_mantenimiento_sin_detalles():
    text = "Busco un ingeniero de mantenimiento para planta industrial."
    result = parse_query(text)

    assert result.role is not None
    assert "ingeniero de mantenimiento" in result.role.lower()
    assert result.years_experience is None
    assert result.num_candidates is None


def test_parse_detecta_skills_basicas():
    text = "Requiero un ingeniero de mantenimiento con experiencia en mantenimiento preventivo y correctivo."
    result = parse_query(text)

    assert any("mantenimiento preventivo" == s.lower() for s in result.skills)
    assert any("mantenimiento correctivo" == s.lower() for s in result.skills)


def test_parse_sample_queries_csv():
    """Valida el parser contra algunas filas del CSV de ejemplo.

    No exige coincidencia perfecta, solo comprueba que los campos
    principales se llenen de forma coherente para el caso de
    "ingeniero de mantenimiento".
    """

    import csv
    from pathlib import Path

    csv_path = Path("data") / "sample_queries.csv"
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Nos centramos en algunas filas de ingeniero de mantenimiento
    subset = [r for r in rows if r["role"].startswith("ingeniero de mantenimiento")][:3]
    assert subset, "No se encontraron filas de ingeniero de mantenimiento en el CSV"

    for row in subset:
        parsed = parse_query(row["query_text"])

        # Rol debe ser algún tipo de ingeniero de mantenimiento
        assert parsed.role is not None
        assert "ingeniero" in parsed.role.lower()
        assert "mantenimiento" in parsed.role.lower()

        # Si el CSV tiene ciudad, esperamos detectar al menos esa ciudad
        if row["location"]:
            assert parsed.location == row["location"]