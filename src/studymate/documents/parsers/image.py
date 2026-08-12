"""Image 'parser'.

Images have no extractable text layer, so this returns a single empty
page - the OCR service is responsible for filling in the text, keeping
OCR concerns out of the parser layer.
"""
from __future__ import annotations

from pathlib import Path

from studymate.documents.parsers.base import ParsedPage


class ImageParser:
    def parse(self, filepath: Path) -> list[ParsedPage]:
        return [ParsedPage(page_number=1, text="")]
