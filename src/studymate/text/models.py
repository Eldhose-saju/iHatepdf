"""Lightweight value object used between chunker and embeddings/search."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ChunkCandidate:
    page_id: int
    chunk_index: int
    text: str
