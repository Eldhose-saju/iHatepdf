"""Keyword search: SQL LIKE matching plus a simple term-frequency score.

Good for exact terminology, formulas, names, identifiers - anything a
semantic embedding might blur (skills.md Skill 7).
"""
from __future__ import annotations

import re
from pathlib import Path

from studymate.db import database

_TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def keyword_search(db_path: Path, query: str, top_k: int = 5) -> list[dict]:
    """Return chunks matching any query token, scored by term frequency.

    Each result: {chunk_id, document, page_number, text, score}
    """
    query_tokens = set(_tokenize(query))
    if not query_tokens:
        return []

    like_clauses = " OR ".join(["c.text LIKE ?"] * len(query_tokens))
    params = [f"%{token}%" for token in query_tokens]

    sql = f"""
        SELECT c.id AS chunk_id, c.text AS text, p.page_number AS page_number,
               d.id AS document_id, d.filename AS filename
        FROM chunks c
        JOIN pages p ON c.page_id = p.id
        JOIN documents d ON p.document_id = d.id
        WHERE {like_clauses}
    """

    with database.session(db_path) as conn:
        rows = conn.execute(sql, params).fetchall()

    results = []
    for row in rows:
        tokens = _tokenize(row["text"])
        if not tokens:
            continue
        matches = sum(1 for t in tokens if t in query_tokens)
        score = matches / len(tokens)
        if score <= 0:
            continue
        results.append({
            "chunk_id": row["chunk_id"],
            "document_id": row["document_id"],
            "filename": row["filename"],
            "page_number": row["page_number"],
            "text": row["text"],
            "score": score,
        })

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top_k]
