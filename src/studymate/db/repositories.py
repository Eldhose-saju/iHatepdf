"""CRUD functions for documents, pages, and chunks.

Each function opens its own short-lived connection via db.database.session.
This keeps the persistence layer simple and avoids sharing connections
across Streamlit reruns/threads.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from studymate.db import database
from studymate.db.models import Chunk, Document, Page


# ---------- Documents ----------

def create_document(db_path: Path, doc: Document) -> int:
    with database.session(db_path) as conn:
        cur = conn.execute(
            """INSERT INTO documents
               (filename, filepath, file_size, file_type, pages, author,
                upload_date, status, error_message)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (doc.filename, doc.filepath, doc.file_size, doc.file_type, doc.pages,
             doc.author, doc.upload_date, doc.status, doc.error_message),
        )
        return int(cur.lastrowid)


def update_document_status(db_path: Path, document_id: int, status: str,
                            error_message: Optional[str] = None) -> None:
    with database.session(db_path) as conn:
        conn.execute(
            "UPDATE documents SET status = ?, error_message = ? WHERE id = ?",
            (status, error_message, document_id),
        )


def update_document_pages(db_path: Path, document_id: int, pages: int) -> None:
    with database.session(db_path) as conn:
        conn.execute("UPDATE documents SET pages = ? WHERE id = ?", (pages, document_id))


def get_document(db_path: Path, document_id: int) -> Optional[Document]:
    with database.session(db_path) as conn:
        row = conn.execute("SELECT * FROM documents WHERE id = ?", (document_id,)).fetchone()
        return _row_to_document(row) if row else None


def list_documents(db_path: Path) -> list[Document]:
    with database.session(db_path) as conn:
        rows = conn.execute("SELECT * FROM documents ORDER BY id DESC").fetchall()
        return [_row_to_document(r) for r in rows]


def delete_document(db_path: Path, document_id: int) -> None:
    with database.session(db_path) as conn:
        conn.execute("DELETE FROM documents WHERE id = ?", (document_id,))


# ---------- Pages ----------

def create_page(db_path: Path, page: Page) -> int:
    with database.session(db_path) as conn:
        cur = conn.execute(
            """INSERT INTO pages (document_id, page_number, extracted_text, ocr_used)
               VALUES (?, ?, ?, ?)""",
            (page.document_id, page.page_number, page.extracted_text, int(page.ocr_used)),
        )
        return int(cur.lastrowid)


def list_pages(db_path: Path, document_id: int) -> list[Page]:
    with database.session(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM pages WHERE document_id = ? ORDER BY page_number", (document_id,)
        ).fetchall()
        return [_row_to_page(r) for r in rows]


def get_page(db_path: Path, page_id: int) -> Optional[Page]:
    with database.session(db_path) as conn:
        row = conn.execute("SELECT * FROM pages WHERE id = ?", (page_id,)).fetchone()
        return _row_to_page(row) if row else None


# ---------- Chunks ----------

def create_chunk(db_path: Path, chunk: Chunk) -> int:
    with database.session(db_path) as conn:
        cur = conn.execute(
            """INSERT INTO chunks (page_id, chunk_index, text, embedded)
               VALUES (?, ?, ?, ?)""",
            (chunk.page_id, chunk.chunk_index, chunk.text, int(chunk.embedded)),
        )
        return int(cur.lastrowid)


def bulk_create_chunks(db_path: Path, chunks: list[Chunk]) -> list[int]:
    ids = []
    with database.session(db_path) as conn:
        for c in chunks:
            cur = conn.execute(
                """INSERT INTO chunks (page_id, chunk_index, text, embedded)
                   VALUES (?, ?, ?, ?)""",
                (c.page_id, c.chunk_index, c.text, int(c.embedded)),
            )
            ids.append(int(cur.lastrowid))
    return ids


def mark_chunks_embedded(db_path: Path, chunk_ids: list[int]) -> None:
    if not chunk_ids:
        return
    with database.session(db_path) as conn:
        conn.executemany("UPDATE chunks SET embedded = 1 WHERE id = ?", [(cid,) for cid in chunk_ids])


def get_chunk(db_path: Path, chunk_id: int) -> Optional[Chunk]:
    with database.session(db_path) as conn:
        row = conn.execute("SELECT * FROM chunks WHERE id = ?", (chunk_id,)).fetchone()
        return _row_to_chunk(row) if row else None


def get_chunks_by_ids(db_path: Path, chunk_ids: list[int]) -> list[Chunk]:
    if not chunk_ids:
        return []
    placeholders = ",".join("?" for _ in chunk_ids)
    with database.session(db_path) as conn:
        rows = conn.execute(
            f"SELECT * FROM chunks WHERE id IN ({placeholders})", chunk_ids
        ).fetchall()
        by_id = {r["id"]: _row_to_chunk(r) for r in rows}
        return [by_id[cid] for cid in chunk_ids if cid in by_id]


def list_all_chunks(db_path: Path) -> list[Chunk]:
    with database.session(db_path) as conn:
        rows = conn.execute("SELECT * FROM chunks").fetchall()
        return [_row_to_chunk(r) for r in rows]


def chunk_source_info(db_path: Path, chunk_id: int) -> Optional[dict]:
    """Return document/page info for a chunk, for source attribution."""
    with database.session(db_path) as conn:
        row = conn.execute(
            """SELECT c.id AS chunk_id, c.text AS text, p.page_number AS page_number,
                      d.id AS document_id, d.filename AS filename
               FROM chunks c
               JOIN pages p ON c.page_id = p.id
               JOIN documents d ON p.document_id = d.id
               WHERE c.id = ?""",
            (chunk_id,),
        ).fetchone()
        return dict(row) if row else None


# ---------- Dashboard counts ----------

def counts(db_path: Path) -> dict:
    with database.session(db_path) as conn:
        doc_count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        page_count = conn.execute("SELECT COUNT(*) FROM pages").fetchone()[0]
        chunk_count = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        indexed_count = conn.execute(
            "SELECT COUNT(*) FROM documents WHERE status = 'indexed'"
        ).fetchone()[0]
        return {
            "documents": doc_count,
            "pages": page_count,
            "chunks": chunk_count,
            "indexed_documents": indexed_count,
        }


# ---------- Row conversion ----------

def _row_to_document(row: sqlite3.Row) -> Document:
    return Document(
        id=row["id"], filename=row["filename"], filepath=row["filepath"],
        file_size=row["file_size"], file_type=row["file_type"], pages=row["pages"],
        author=row["author"], upload_date=row["upload_date"], status=row["status"],
        error_message=row["error_message"],
    )


def _row_to_page(row: sqlite3.Row) -> Page:
    return Page(
        id=row["id"], document_id=row["document_id"], page_number=row["page_number"],
        extracted_text=row["extracted_text"], ocr_used=bool(row["ocr_used"]),
    )


def _row_to_chunk(row: sqlite3.Row) -> Chunk:
    return Chunk(
        id=row["id"], page_id=row["page_id"], chunk_index=row["chunk_index"],
        text=row["text"], embedded=bool(row["embedded"]),
    )
