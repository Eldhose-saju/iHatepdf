"""Small helpers for deriving document metadata."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


def file_type_of(filename: str) -> str:
    return Path(filename).suffix.lower().lstrip(".")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
