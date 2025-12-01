import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "candidatos.db")
CANDIDATES_CSV_PATH = os.path.join(BASE_DIR, "data", "candidatos.csv")
SAMPLE_QUERIES_PATH = os.path.join(BASE_DIR, "data", "sample_queries.csv")
EVAL_QUERIES_PATH = os.path.join(BASE_DIR, "data", "evaluacion.csv")