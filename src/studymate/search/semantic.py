"""Semantic search over the persisted vector index.

Good for paraphrased questions and conceptual queries that share no
exact words with the source text (skills.md Skill 7).
"""
from __future__ import annotations

from pathlib import Path

from studymate.db import repositories as repo
from studymate.embeddings.service import EmbeddingModel
from studymate.search.index import VectorIndex


def semantic_search(
    db_path: Path, index: VectorIndex, embedder: EmbeddingModel, query: str, top_k: int = 5
) -> list[dict]:
    """Return [{chunk_id, document, page_number, text, score}, ...]."""
    if index.size() == 0:
        return []

    query_vector = embedder.embed([query])[0]
    hits = index.search(query_vector, top_k=top_k)
    if not hits:
        return []

    chunk_ids = [chunk_id for chunk_id, _ in hits]
    sources = {info["chunk_id"]: info for info in
               (repo.chunk_source_info(db_path, cid) for cid in chunk_ids) if info}

    results = []
    for chunk_id, score in hits:
        info = sources.get(chunk_id)
        if not info:
            continue  # vector referenced a chunk that no longer exists
        results.append({
            "chunk_id": chunk_id,
            "document_id": info["document_id"],
            "filename": info["filename"],
            "page_number": info["page_number"],
            "text": info["text"],
            "score": score,
        })
    return results
