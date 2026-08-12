"""Text normalization for retrieval-ready content."""
from __future__ import annotations

import re

_MULTI_SPACE = re.compile(r"[ \t]+")
_MULTI_BLANK_LINE = re.compile(r"\n{3,}")
_HYPHEN_LINEBREAK = re.compile(r"(\w)-\n(\w)")  # "informa-\ntion" -> "information"


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _HYPHEN_LINEBREAK.sub(r"\1\2", text)
    text = _MULTI_SPACE.sub(" ", text)
    text = _MULTI_BLANK_LINE.sub("\n\n", text)
    lines = [line.strip() for line in text.split("\n")]
    return "\n".join(lines).strip()
