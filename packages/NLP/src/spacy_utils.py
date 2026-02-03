from functools import lru_cache
from typing import Iterable

import spacy
from spacy.language import Language
from spacy.tokens import Doc


@lru_cache(maxsize=1)
def load_spacy_model(model_name: str = "es_core_news_md") -> Language:
	"""Carga y cachea el modelo de spaCy para español.

	Parameters
	----------
	model_name:
		Nombre del modelo spaCy instalado. Para la PoC se asume
		un modelo de español como ``es_core_news_md``.
	"""

	return spacy.load(model_name)


def get_doc(text: str, model_name: str = "es_core_news_md") -> Doc:
	"""Crea un ``Doc`` de spaCy a partir de un texto en español."""

	nlp = load_spacy_model(model_name=model_name)
	return nlp(text)


def iter_noun_chunks(doc: Doc) -> Iterable[str]:
	"""Devuelve los *noun chunks* del documento como cadenas.

	Útil para detectar posibles spans de rol como
	"ingeniero de mantenimiento".
	"""

	for chunk in doc.noun_chunks:
		yield chunk.text


__all__ = ["load_spacy_model", "get_doc", "iter_noun_chunks"]

