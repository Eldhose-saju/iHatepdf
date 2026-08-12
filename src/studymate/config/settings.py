"""Centralized configuration. Reads from environment with sane defaults.

Only the settings actually used by the application are defined here -
no speculative configuration framework.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _env_path(name: str, default: Path) -> Path:
    value = os.getenv(name)
    return Path(value) if value else default


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    try:
        return int(value) if value else default
    except ValueError:
        return default


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    data_dir: Path = field(default_factory=lambda: _env_path("DATA_DIR", PROJECT_ROOT / "data"))
    upload_dir: Path = field(default_factory=lambda: _env_path("UPLOAD_DIR", PROJECT_ROOT / "data" / "uploads"))
    processed_dir: Path = field(default_factory=lambda: _env_path("PROCESSED_DIR", PROJECT_ROOT / "data" / "processed"))
    vector_dir: Path = field(default_factory=lambda: _env_path("VECTOR_DIR", PROJECT_ROOT / "data" / "vectors"))
    database_path: Path = field(default_factory=lambda: _env_path("DATABASE_PATH", PROJECT_ROOT / "data" / "studymate.db"))

    embedding_model: str = field(default_factory=lambda: os.getenv("EMBEDDING_MODEL", "hashing-384"))
    llm_provider: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "ollama"))
    llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "llama3.1"))
    ollama_host: str = field(default_factory=lambda: os.getenv("OLLAMA_HOST", "http://localhost:11434"))

    chunk_size: int = field(default_factory=lambda: _env_int("CHUNK_SIZE", 800))
    chunk_overlap: int = field(default_factory=lambda: _env_int("CHUNK_OVERLAP", 120))
    top_k: int = field(default_factory=lambda: _env_int("TOP_K", 5))
    ocr_enabled: bool = field(default_factory=lambda: _env_bool("OCR_ENABLED", True))

    max_upload_mb: int = field(default_factory=lambda: _env_int("MAX_UPLOAD_MB", 50))

    def ensure_dirs(self) -> None:
        for path in (self.data_dir, self.upload_dir, self.processed_dir, self.vector_dir):
            path.mkdir(parents=True, exist_ok=True)


_settings: Settings | None = None


def get_settings() -> Settings:
    """Return the process-wide Settings singleton, creating dirs on first access."""
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.ensure_dirs()
    return _settings
