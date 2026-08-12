"""Upload validation. Kept as plain functions - no framework needed."""
from __future__ import annotations

from pathlib import Path

from studymate.config.settings import Settings
from studymate.utils.files import is_supported


class ValidationError(Exception):
    """Raised when an upload fails validation."""


def validate_upload(filename: str, file_size: int, settings: Settings) -> None:
    if not filename or not filename.strip():
        raise ValidationError("Filename is empty.")

    if not is_supported(filename):
        ext = Path(filename).suffix or "(none)"
        raise ValidationError(
            f"Unsupported file type '{ext}'. Supported: PDF, DOCX, PPTX, and common image formats."
        )

    if file_size <= 0:
        raise ValidationError("File is empty (0 bytes).")

    max_bytes = settings.max_upload_mb * 1024 * 1024
    if file_size > max_bytes:
        raise ValidationError(
            f"File is too large ({file_size / 1_048_576:.1f} MB). Max is {settings.max_upload_mb} MB."
        )
