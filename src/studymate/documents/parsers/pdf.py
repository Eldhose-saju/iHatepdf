"""PDF text extraction using pypdf."""
from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from studymate.documents.parsers.base import ParsedPage


class PDFParser:
    def parse(self, filepath: Path) -> list[ParsedPage]:
        reader = PdfReader(str(filepath))
        pages: list[ParsedPage] = []
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            pages.append(ParsedPage(page_number=i, text=text))
        return pages
