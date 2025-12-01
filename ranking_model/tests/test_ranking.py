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

