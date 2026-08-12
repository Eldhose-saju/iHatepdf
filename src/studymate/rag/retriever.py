"""Retrieval step of RAG: thin wrapper over SearchService.

Kept as its own module (rather than inlined in rag/service.py) so
retrieval is independently testable from generation, per skills.md
Skill 8 ("keep retrieval and generation independently testable").
"""
from __future__ import annotations

from studymate.search.service import SearchService

# Hybrid scores are min-max normalized within each query's own result set,
# so they carry no absolute meaning (a lone weak match still normalizes to
# 1.0 - see search/hybrid.py). Evidence sufficiency therefore has to be
# judged on semantic search's raw, un-normalized cosine similarity instead.
MIN_RELEVANCE_SCORE = 0.15


def retrieve(search_service: SearchService, question: str, top_k: int | None = None) -> list[dict]:
    return search_service.search(question, mode="hybrid", top_k=top_k)


def top_raw_semantic_score(search_service: SearchService, question: str) -> float:
    """Un-normalized cosine similarity of the single best semantic match."""
    raw = search_service.search(question, mode="semantic", top_k=1)
    return raw[0]["score"] if raw else 0.0


def has_sufficient_evidence(raw_score: float) -> bool:
    return raw_score >= MIN_RELEVANCE_SCORE
