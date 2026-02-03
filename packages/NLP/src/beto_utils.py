from functools import lru_cache
from typing import Dict, Iterable, List, Tuple

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer


BETO_MODEL_NAME = "dccuchile/bert-base-spanish-wwm-cased"


@lru_cache(maxsize=1)
def load_beto() -> Tuple[AutoTokenizer, AutoModel]:
	"""Carga y cachea el modelo BETO desde Hugging Face.

	Se usa sin *fine-tuning* para obtener representaciones
	semánticas simples de texto.
	"""

	tokenizer = AutoTokenizer.from_pretrained(BETO_MODEL_NAME)
	model = AutoModel.from_pretrained(BETO_MODEL_NAME)
	model.eval()
	return tokenizer, model


def _to_numpy(tensor: torch.Tensor) -> np.ndarray:
	return tensor.detach().cpu().numpy()


def embed_text(text: str) -> np.ndarray:
	"""Obtiene un embedding denso para ``text`` usando BETO.

	Estrategia simple: vector CLS de la última capa.
	"""

	tokenizer, model = load_beto()
	encoded = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
	with torch.no_grad():
		output = model(**encoded)
	cls_embedding = output.last_hidden_state[:, 0, :].squeeze(0)
	return _to_numpy(cls_embedding)


def precompute_catalog_embeddings(items: Iterable[str]) -> Dict[str, np.ndarray]:
	"""Devuelve un diccionario item -> embedding BETO."""

	return {item: embed_text(item) for item in items}


def most_similar(
	text: str,
	catalog_embeddings: Dict[str, np.ndarray],
	top_k: int = 1,
) -> List[Tuple[str, float]]:
	"""Devuelve los ``top_k`` items más similares al ``text``.

	Se usa similitud coseno entre el embedding del texto y los
	embeddings precomputados del catálogo.
	"""

	if not catalog_embeddings:
		return []

	query_vec = embed_text(text)
	query_norm = np.linalg.norm(query_vec) or 1.0

	sims: List[Tuple[str, float]] = []
	for label, vec in catalog_embeddings.items():
		denom = (np.linalg.norm(vec) or 1.0) * query_norm
		score = float(np.dot(query_vec, vec) / denom)
		sims.append((label, score))

	sims.sort(key=lambda x: x[1], reverse=True)
	return sims[:top_k]


__all__ = [
	"BETO_MODEL_NAME",
	"load_beto",
	"embed_text",
	"precompute_catalog_embeddings",
	"most_similar",
]

