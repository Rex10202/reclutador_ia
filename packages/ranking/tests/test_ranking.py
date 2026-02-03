import os
from pathlib import Path
from ranking_model.src.ranking_orchestrator import RankingOrchestrator
from ranking_model.src.ranking_engine import RankingQueryRequirements
from src.ranking_features import QueryRequirements
from src.ranking_engine import load_candidates, rank_candidates


def test_rank_maintenance_engineer_cartagena():
	"""C03 debería estar entre los primeros para una consulta típica."""

	query = QueryRequirements(
		role="ingeniero de mantenimiento",
		skills=["mantenimiento preventivo", "mantenimiento correctivo", "gestión de repuestos"],
		location="Cartagena",
		years_experience=3,
		languages=["inglés"],
	)

	candidates = load_candidates()
	results = rank_candidates(query, candidates, limit=3)
	ids = [r["id"] for r in results]

	assert "C03" in ids
	assert ids.index("C03") == 0

def test_ranking_basic():
    # Asegura que el CSV exista
    base_dir = Path(__file__).resolve().parents[1]
    csv_path = base_dir / "data" / "candidates.csv"
    assert csv_path.exists(), f"No se encontró {csv_path}"

    orchestrator = RankingOrchestrator()

    req = RankingQueryRequirements(
        role="técnico de mantenimiento",
        location="Cartagena",
        years_experience=3,
        skills=[
            "mantenimiento preventivo",
            "mantenimiento correctivo",
            "hidráulica",
            "neumática",
            "mecánica industrial",
            "electricidad industrial",
        ],
    )

    ranked = orchestrator.run_ranking(req, num_candidates=5)
    # Sólo comprobar que no revienta y devuelve lista
    assert isinstance(ranked, list)
    if ranked:
        c0 = ranked[0]
        assert hasattr(c0, "id")
        assert hasattr(c0, "score")