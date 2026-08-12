"""Deterministic fixed-size chunking with overlap.

Deliberately simple word-count-based chunking (Skill 5: avoid complex
semantic chunking until a measurable requirement exists). Output is
deterministic for identical input/settings, and never emits empty
chunks.
"""
from __future__ import annotations

from studymate.text.models import ChunkCandidate


def chunk_text(page_id: int, text: str, chunk_size: int = 800, chunk_overlap: int = 120) -> list[ChunkCandidate]:
    """Split text into overlapping chunks, measured in characters.

    chunk_overlap must be smaller than chunk_size or the loop cannot progress.
    """
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    text = text.strip()
    if not text:
        return []

    chunks: list[ChunkCandidate] = []
    start = 0
    index = 0
    length = len(text)
    step = chunk_size - chunk_overlap

    while start < length:
        end = min(start + chunk_size, length)
        piece = text[start:end].strip()
        if piece:
            chunks.append(ChunkCandidate(page_id=page_id, chunk_index=index, text=piece))
            index += 1
        if end == length:
            break
        start += step

    return chunks
