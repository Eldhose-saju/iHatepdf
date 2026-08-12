"""Small file-system helpers shared across services."""
from __future__ import annotations

import shutil
import uuid
from pathlib import Path

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}


def is_supported(filename: str) -> bool:
    return Path(filename).suffix.lower() in SUPPORTED_EXTENSIONS


def is_image(filename: str) -> bool:
    return Path(filename).suffix.lower() in IMAGE_EXTENSIONS


def unique_storage_name(filename: str) -> str:
    """A collision-free filename that keeps the original extension."""
    suffix = Path(filename).suffix.lower()
    return f"{uuid.uuid4().hex}{suffix}"


def save_upload(src_path: Path, upload_dir: Path, original_filename: str) -> Path:
    """Copy a file into the upload directory under a unique name and return its path."""
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest = upload_dir / unique_storage_name(original_filename)
    shutil.copyfile(src_path, dest)
    return dest
