"""Shared helpers for study-tool generators."""
from __future__ import annotations

import json
import re


def strip_json_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    return text


def safe_parse_json(text: str):
    """Parse LLM JSON output, returning None on failure instead of raising.

    LLM output is not guaranteed to be well-formed JSON; callers must
    handle None and fall back gracefully rather than crashing the UI.
    """
    try:
        return json.loads(strip_json_fences(text))
    except json.JSONDecodeError:
        return None
