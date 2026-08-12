"""Shared test helpers (not a pytest conftest.py - imported explicitly
by test modules so tests also run under plain `python -m unittest`
without requiring pytest to be installed).
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from studymate.config.settings import Settings  # noqa: E402


def make_test_settings(tmp_dir: Path) -> Settings:
    settings = Settings(
        data_dir=tmp_dir,
        upload_dir=tmp_dir / "uploads",
        processed_dir=tmp_dir / "processed",
        vector_dir=tmp_dir / "vectors",
        database_path=tmp_dir / "test.db",
        embedding_model="hashing-64",
        chunk_size=200,
        chunk_overlap=40,
        top_k=5,
        ocr_enabled=False,  # keep unit tests fast/deterministic; OCR tested separately
    )
    settings.ensure_dirs()
    return settings


class FakeLLM:
    """Deterministic stand-in LLM adapter for tests - no network, no model."""

    def __init__(self, response: str = ""):
        self.response = response
        self.calls: list[tuple[str, str | None]] = []

    def generate(self, prompt: str, system: str | None = None) -> str:
        self.calls.append((prompt, system))
        return self.response
