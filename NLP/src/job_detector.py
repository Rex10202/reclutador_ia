import os
import re
import unicodedata
import warnings
from typing import Any
import torch
import torch.nn.functional as F
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from transformers.utils import logging as hf_logging

# ---------------------------------------------------------
# 1) Apagar warnings de Hugging Face / transformers
# ---------------------------------------------------------

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
hf_logging.set_verbosity_error()

warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    module="huggingface_hub.file_download",
)

# ---------------------------------------------------------
# 2) Carga LAZY del modelo zero-shot
# ---------------------------------------------------------

MODEL_NAME = "joeddav/xlm-roberta-large-xnli"
LABEL_ENTAILMENT = 2  # 0: contradiction, 1: neutral, 2: entailment

_tokenizer = None
_model = None


def _load_nli_model():
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        _model.eval()
    return _tokenizer, _model


def _safe_text(text: Any) -> str:
    if not isinstance(text, str):
        return ""
    return text.strip()


# ---------------------------------------------------------
# 3) Normalización sin tildes + palabras clave de "trabajo"
# ---------------------------------------------------------

def _normalize_no_accents(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text.lower()


JOB_KEYWORDS_PATTERN = re.compile(
    r"\b("
    r"ingeniero?s?|ingeniera?s?|"
    r"tecnico?s?|tecnica?s?|"
    r"analista?s?|"
    r"desarrollador(?:a|es)?|"
    r"programador(?:a|es)?|"
    r"practicante?s?|"
    r"auxiliar(?:es)?|"
    r"coordinador(?:a|es)?|"
    r"operario?s?|operaria?s?|"
    r"jefe?s?|"
    r"gerente?s?|"
    r"director(?:a|es)?|"
    r"arquitecto?s?|arquitecta?s?|"
    r"enfermero?s?|enfermera?s?|"
    r"medico?s?|medica?s?|"
    r"abogado?s?|abogada?s?"
    r")\b"
)


def _heuristic_es_trabajo(texto: str) -> bool:
    if not texto:
        return False
    norm = _normalize_no_accents(texto)
    return JOB_KEYWORDS_PATTERN.search(norm) is not None


# ---------------------------------------------------------
# 4) Score NLI + función pública
# ---------------------------------------------------------

def score_es_trabajo(texto: str) -> float:

    texto = _safe_text(texto)
    if not texto:
        return 0.0

    tokenizer, model = _load_nli_model()

    premisa = texto
    hipotesis = "Este texto describe un trabajo."

    inputs = tokenizer(premisa, hipotesis, return_tensors="pt", truncation=True)
    with torch.no_grad():
        logits = model(**inputs).logits

    probs = F.softmax(logits, dim=-1)[0]
    p_entail = probs[LABEL_ENTAILMENT].item()
    return float(p_entail)


def es_trabajo(texto: str, umbral: float = 0.35) -> bool:
    texto = _safe_text(texto)
    if not texto:
        return False

    if _heuristic_es_trabajo(texto):
        return True

    return score_es_trabajo(texto) >= umbral


__all__ = ["score_es_trabajo", "es_trabajo"]
