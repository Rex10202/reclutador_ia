from __future__ import annotations

from functools import lru_cache
from typing import Iterable, List

import numpy as np
from sentence_transformers import SentenceTransformer

from .config import SENTENCE_TRANSFORMER_MODEL_NAME


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    """
    Carga el modelo de sentence-transformers una sola vez (singleton con cache).
    """
    return SentenceTransformer(SENTENCE_TRANSFORMER_MODEL_NAME)


def get_embeddings(texts: Iterable[str]) -> np.ndarray:
    """
    Devuelve un array numpy (n_samples, dim) con los embeddings de cada texto.
    No normaliza por defecto; la normalización se hace en la similitud de coseno.
    """
    model = _get_model()
    # SentenceTransformers ya maneja batching internamente
    embeddings = model.encode(
        list(texts),
        convert_to_numpy=True,
        normalize_embeddings=False,
        show_progress_bar=False,
    )
    return embeddings.astype("float32")


def cosine_sim(query_vec: np.ndarray, cand_matrix: np.ndarray) -> np.ndarray:
    """
    Calcula similitud de coseno entre un vector de consulta (dim,)
    y una matriz de candidatos (n, dim) -> (n,).
    """
    # Asegurar dimensiones
    if query_vec.ndim == 1:
        query_vec = query_vec[None, :]  # (1, dim)

    # Normaliza
    q_norm = query_vec / (np.linalg.norm(query_vec, axis=1, keepdims=True) + 1e-12)
    c_norm = cand_matrix / (np.linalg.norm(cand_matrix, axis=1, keepdims=True) + 1e-12)

    # Producto punto (1, dim) x (dim, n) -> (1, n)
    sims = np.dot(q_norm, c_norm.T)[0]
    return sims