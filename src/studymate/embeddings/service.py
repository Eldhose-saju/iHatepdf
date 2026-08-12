"""Local embedding generation.

Uses sentence-transformers when it is installed (set EMBEDDING_MODEL to
a real model name, e.g. "all-MiniLM-L6-v2"). When it is not available,
falls back to a deterministic hashing bag-of-words vectorizer that needs
no model download - this keeps the app genuinely offline-first without
a mandatory dependency, per agent.md Section 8 ("do not implement
multiple providers until one works correctly" - the fallback IS the one
provider guaranteed to work everywhere).

Swapping in sentence-transformers later requires no changes outside
this file: both paths implement the same embed(texts) -> np.ndarray contract.
"""
from __future__ import annotations

import hashlib
import re
from typing import Protocol

import numpy as np

from studymate.utils.logging import get_logger

logger = get_logger(__name__)

_TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")


class EmbeddingModel(Protocol):
    dimension: int

    def embed(self, texts: list[str]) -> np.ndarray:
        ...


class HashingEmbedder:
    """Deterministic, dependency-free bag-of-words embedder.

    Each token is hashed into a fixed-size vector (a simplified
    "hashing trick" vectorizer), then L2-normalized so cosine similarity
    behaves sensibly. Not as semantically rich as a trained model, but
    fully local, fully offline, and stable across restarts.
    """

    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def embed(self, texts: list[str]) -> np.ndarray:
        vectors = np.zeros((len(texts), self.dimension), dtype=np.float32)
        for i, text in enumerate(texts):
            tokens = _TOKEN_RE.findall(text.lower())
            for token in tokens:
                idx = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16) % self.dimension
                vectors[i, idx] += 1.0
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return vectors / norms


class SentenceTransformerEmbedder:
    """Thin wrapper around sentence-transformers, used only if installed."""

    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer  # local import: optional dep

        self._model = SentenceTransformer(model_name)
        self.dimension = self._model.get_sentence_embedding_dimension()

    def embed(self, texts: list[str]) -> np.ndarray:
        vectors = self._model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        return vectors.astype(np.float32)


def get_embedder(model_name: str) -> EmbeddingModel:
    if model_name.startswith("hashing"):
        dim = 384
        if "-" in model_name:
            try:
                dim = int(model_name.rsplit("-", 1)[1])
            except ValueError:
                pass
        return HashingEmbedder(dimension=dim)

    try:
        return SentenceTransformerEmbedder(model_name)
    except ImportError:
        logger.warning(
            "sentence-transformers not installed; falling back to local hashing embedder. "
            "Install sentence-transformers and set EMBEDDING_MODEL to use a trained model."
        )
        return HashingEmbedder(dimension=384)
