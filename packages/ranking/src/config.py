import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
CANDIDATES_CSV_PATH = BASE_DIR / "data" / "candidates.csv"
DEFAULT_TOP_N = 50
SENTENCE_TRANSFORMER_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"