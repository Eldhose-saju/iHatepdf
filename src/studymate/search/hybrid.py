"""Hybrid search: a simple, deterministic weighted combination.

No learning-to-rank - just normalized-score blending, per agent.md
Section 9 ("keep ranking logic simple and deterministic").
"""
from __future__ import annotations

from pathlib import Path

from studymate.embeddings.service import EmbeddingModel
from studymate.search.index import VectorIndex
from studymate.search.keyword import keyword_search
from studymate.search.semantic import semantic_search


def _normalize(results: list[dict]) -> dict[int, float]:
    """Min-max normalize scores to [0, 1].

    When every result has the same score (including the single-result
    case), min == max: rather than collapsing everyone to 0 (which would
    make a lone, possibly strong match look like the worst possible
    match), treat all tied results as equally maximally relevant.
    """
    if not results:
        return {}
    scores = [r["score"] for r in results]
    lo, hi = min(scores), max(scores)
    if hi == lo:
        return {r["chunk_id"]: 1.0 for r in results}
    span = hi - lo
    return {r["chunk_id"]: (r["score"] - lo) / span for r in results}


def hybrid_search(
    db_path: Path,
    index: VectorIndex,
    embedder: EmbeddingModel,
    query: str,
    top_k: int = 5,
    keyword_weight: float = 0.4,
    semantic_weight: float = 0.6,
) -> list[dict]:
    keyword_results = keyword_search(db_path, query, top_k=max(top_k * 3, 10))
    semantic_results = semantic_search(db_path, index, embedder, query, top_k=max(top_k * 3, 10))

    by_chunk: dict[int, dict] = {}
    for r in keyword_results + semantic_results:
        by_chunk.setdefault(r["chunk_id"], r)

    kw_norm = _normalize(keyword_results)
    sem_norm = _normalize(semantic_results)

    scored = []
    for chunk_id, base in by_chunk.items():
        combined = keyword_weight * kw_norm.get(chunk_id, 0.0) + semantic_weight * sem_norm.get(chunk_id, 0.0)
        scored.append({**base, "score": combined})

    scored.sort(key=lambda r: r["score"], reverse=True)
    return scored[:top_k]
