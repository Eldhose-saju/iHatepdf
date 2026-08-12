"""Local vector index: persisted numpy matrix + a chunk-ID mapping.

Plays the role faiss-cpu would, at a scale (a student's own documents)
where an in-memory numpy matrix with cosine similarity is genuinely
simpler and just as fast (skills.md Skill 18: avoid premature
infrastructure). Swapping to faiss later only touches this file.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

VECTORS_FILE = "vectors.npy"
MAPPING_FILE = "mapping.json"


class VectorIndexError(Exception):
    """Raised when the persisted index is missing or corrupt."""


class VectorIndex:
    def __init__(self, dimension: int):
        self.dimension = dimension
        self._vectors: np.ndarray = np.zeros((0, dimension), dtype=np.float32)
        self._chunk_ids: list[int] = []

    def add(self, vectors: np.ndarray, chunk_ids: list[int]) -> None:
        if vectors.shape[0] != len(chunk_ids):
            raise ValueError("vectors and chunk_ids must have the same length")
        if vectors.shape[1] != self.dimension:
            raise ValueError(f"expected dimension {self.dimension}, got {vectors.shape[1]}")
        self._vectors = np.vstack([self._vectors, vectors.astype(np.float32)])
        self._chunk_ids.extend(chunk_ids)

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> list[tuple[int, float]]:
        """Return [(chunk_id, similarity_score), ...] sorted by score descending."""
        if len(self._chunk_ids) == 0:
            return []
        query_vector = query_vector.reshape(1, -1).astype(np.float32)
        # vectors are pre-normalized at embed time, so dot product == cosine similarity
        scores = (self._vectors @ query_vector.T).ravel()
        top_k = min(top_k, len(scores))
        top_indices = np.argsort(-scores)[:top_k]
        return [(self._chunk_ids[i], float(scores[i])) for i in top_indices]

    def size(self) -> int:
        return len(self._chunk_ids)

    def save(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        np.save(directory / VECTORS_FILE, self._vectors)
        (directory / MAPPING_FILE).write_text(
            json.dumps({"dimension": self.dimension, "chunk_ids": self._chunk_ids})
        )

    @classmethod
    def load(cls, directory: Path) -> "VectorIndex":
        vectors_path = directory / VECTORS_FILE
        mapping_path = directory / MAPPING_FILE
        if not vectors_path.exists() or not mapping_path.exists():
            raise VectorIndexError(f"No index found at {directory}")
        try:
            mapping = json.loads(mapping_path.read_text())
            vectors = np.load(vectors_path)
        except Exception as exc:
            raise VectorIndexError(f"Index at {directory} is corrupt: {exc}") from exc

        index = cls(dimension=mapping["dimension"])
        index._vectors = vectors
        index._chunk_ids = mapping["chunk_ids"]
        return index

    @classmethod
    def load_or_create(cls, directory: Path, dimension: int) -> "VectorIndex":
        try:
            return cls.load(directory)
        except VectorIndexError:
            return cls(dimension=dimension)
