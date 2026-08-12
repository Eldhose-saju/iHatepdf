"""OCR for scanned/image-based content, using pytesseract.

Only runs when a page's extracted text is empty/near-empty (i.e. the
page is actually scanned) - normal text documents never pass through
OCR, per skills.md Skill 4.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

from studymate.utils.logging import get_logger

logger = get_logger(__name__)

# Below this many characters, a "text" page is treated as scanned/empty.
EMPTY_TEXT_THRESHOLD = 10


class OCRError(Exception):
    """Raised when OCR cannot be run or fails outright."""


def needs_ocr(extracted_text: str) -> bool:
    return len(extracted_text.strip()) < EMPTY_TEXT_THRESHOLD


def ocr_image_file(filepath: Path) -> str:
    """Run OCR on a standalone image file and return normalized text."""
    try:
        import pytesseract
    except ImportError as exc:
        raise OCRError("pytesseract is not installed.") from exc

    try:
        image = Image.open(filepath)
        raw_text = pytesseract.image_to_string(image)
    except Exception as exc:  # tesseract binary missing, unreadable image, etc.
        raise OCRError(f"OCR failed for {filepath.name}: {exc}") from exc

    return _normalize(raw_text)


def ocr_pdf_page(filepath: Path, page_number: int) -> str:
    """Rasterize a single PDF page and OCR it. Requires pypdfium2."""
    try:
        import pypdfium2 as pdfium
        import pytesseract
    except ImportError as exc:
        raise OCRError("pypdfium2/pytesseract not installed.") from exc

    try:
        pdf = pdfium.PdfDocument(str(filepath))
        page = pdf[page_number - 1]
        bitmap = page.render(scale=2.0)
        image = bitmap.to_pil()
        raw_text = pytesseract.image_to_string(image)
    except Exception as exc:
        raise OCRError(f"OCR failed for {filepath.name} page {page_number}: {exc}") from exc

    return _normalize(raw_text)


def _normalize(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)
