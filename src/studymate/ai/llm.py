"""LLM adapter interface.

The rest of the app (RAG, study tools) depends only on this Protocol,
never on a specific vendor/runtime - agent.md Section 8 and skills.md
Skill 9 require the UI/RAG layer to stay vendor-independent.
"""
from __future__ import annotations

from typing import Protocol


class LLMUnavailableError(Exception):
    """Raised when no local LLM runtime could be reached."""


class LLMAdapter(Protocol):
    def generate(self, prompt: str, system: str | None = None) -> str:
        """Return a single completion for the given prompt."""
        ...
