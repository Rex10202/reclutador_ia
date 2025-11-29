import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "candidatos.db")
SAMPLE_QUERIES_PATH = os.path.join(BASE_DIR, "data", "sample_queries.csv")
RAW_CSV_PATH = SAMPLE_QUERIES_PATH
MODEL_PATH = os.path.join(BASE_DIR, "models", "modelo_recomendador.joblib")
