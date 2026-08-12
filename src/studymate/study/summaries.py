"""Document/material summaries, generated from selected or retrieved context."""
from __future__ import annotations

from dataclasses import dataclass

from studymate.ai.llm import LLMAdapter, LLMUnavailableError
from studymate.db import repositories as repo
from studymate.config.settings import Settings

SUMMARY_SYSTEM_PROMPT = (
    "You are a study assistant. Write a clear, concise summary of the "
    "provided material for a student reviewing it before an exam. Use "
    "short paragraphs or bullet points. Do not invent facts not present "
    "in the material."
)


@dataclass
class Summary:
    source_label: str
    text: str


def summarize_text(llm: LLMAdapter, text: str, source_label: str) -> Summary:
    prompt = f"Material to summarize:\n\n{text}\n\nWrite a concise summary."
    try:
        summary_text = llm.generate(prompt, system=SUMMARY_SYSTEM_PROMPT)
    except LLMUnavailableError as exc:
        summary_text = f"(LLM unavailable, showing raw excerpt instead: {exc})\n\n{text[:1000]}"
    return Summary(source_label=source_label, text=summary_text)


def summarize_document(settings: Settings, llm: LLMAdapter, document_id: int) -> Summary:
    doc = repo.get_document(settings.database_path, document_id)
    pages = repo.list_pages(settings.database_path, document_id)
    full_text = "\n\n".join(p.extracted_text for p in pages if p.extracted_text.strip())
    if not full_text.strip():
        return Summary(source_label=doc.filename if doc else "unknown",
                        text="This document has no extracted text to summarize.")
    return summarize_text(llm, full_text, source_label=doc.filename if doc else "unknown")


def summarize_selection(llm: LLMAdapter, results: list[dict]) -> Summary:
    """Summarize a set of search/RAG results (Task 9's 'selected material summary')."""
    text = "\n\n".join(r["text"] for r in results)
    label = ", ".join(sorted({r["filename"] for r in results})) or "selected material"
    return summarize_text(llm, text, source_label=label)
