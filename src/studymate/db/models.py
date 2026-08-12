"""Plain dataclasses mirroring the SQLite schema.

Kept intentionally simple - no ORM mapping magic, just typed containers
that repositories.py converts to/from sqlite3.Row.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

# Lifecycle: uploaded -> processing -> processed -> indexed, or -> failed
STATUS_UPLOADED = "uploaded"
STATUS_PROCESSING = "processing"
STATUS_PROCESSED = "processed"
STATUS_INDEXED = "indexed"
STATUS_FAILED = "failed"


@dataclass
class Document:
    id: Optional[int]
    filename: str
    filepath: str
    file_size: int
    file_type: str
    pages: int = 0
    author: Optional[str] = None
    upload_date: str = ""
    status: str = STATUS_UPLOADED
    error_message: Optional[str] = None


@dataclass
class Page:
    id: Optional[int]
    document_id: int
    page_number: int
    extracted_text: str = ""
    ocr_used: bool = False


@dataclass
class Chunk:
    id: Optional[int]
    page_id: int
    chunk_index: int
    text: str
    embedded: bool = False
