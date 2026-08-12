"""Local LLM adapters: Ollama (preferred) and an extractive fallback.

The Ollama adapter talks to a locally running Ollama server over HTTP -
no API key, no cloud dependency. If Ollama isn't running, callers should
catch LLMUnavailableError and fall back to ExtractiveAdapter so the
product still functions (in a reduced way) fully offline with zero
local model installed.
"""
from __future__ import annotations

import requests

from studymate.ai.llm import LLMUnavailableError
from studymate.utils.logging import get_logger

logger = get_logger(__name__)


class OllamaAdapter:
    def __init__(self, host: str, model: str, timeout: int = 120):
        self.host = host.rstrip("/")
        self.model = model
        self.timeout = timeout

    def generate(self, prompt: str, system: str | None = None) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system or "",
            "stream": False,
        }
        try:
            response = requests.post(f"{self.host}/api/generate", json=payload, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise LLMUnavailableError(
                f"Could not reach Ollama at {self.host}. Is `ollama serve` running "
                f"and is model '{self.model}' pulled? ({exc})"
            ) from exc

        data = response.json()
        return (data.get("response") or "").strip()


class ExtractiveAdapter:
    """No-model fallback: returns the retrieved context verbatim (trimmed).

    Used only when no local LLM runtime is reachable, so the app degrades
    to "show me the relevant material" instead of failing outright. Study
    tools should clearly label output produced this way.
    """

    def generate(self, prompt: str, system: str | None = None) -> str:
        return (
            "[No local LLM is available, so this is the most relevant retrieved "
            "text rather than a generated answer. Start an Ollama server and set "
            "LLM_MODEL to enable generated answers.]\n\n" + prompt
        )


def get_llm_adapter(provider: str, model: str, host: str) -> "OllamaAdapter | ExtractiveAdapter":
    if provider == "ollama":
        return OllamaAdapter(host=host, model=model)
    logger.warning("Unknown LLM provider '%s'; using extractive fallback.", provider)
    return ExtractiveAdapter()
