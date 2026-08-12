"""Common parser contract.

A parser turns a file on disk into a list of per-page text strings.
Kept as a simple Protocol (not a heavy plugin framework) since every
parser genuinely shares this one shape.
"""
from __future__ import annotations

from pathlib import Path
from typing import Protocol


class ParsedPage:
    __slots__ = ("page_number", "text", "is_empty")

    def __init__(self, page_number: int, text: str):
        self.page_number = page_number
        self.text = text
        self.is_empty = len(text.strip()) == 0


class DocumentParser(Protocol):
    def parse(self, filepath: Path) -> list[ParsedPage]:
        """Return one ParsedPage per page/slide, 1-indexed."""
        ...
