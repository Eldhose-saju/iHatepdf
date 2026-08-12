"""Concise structured revision notes generated from selected source material."""
from __future__ import annotations

from dataclasses import dataclass

from studymate.ai.llm import LLMAdapter, LLMUnavailableError

REVISION_SYSTEM_PROMPT = (
    "You are a study assistant writing concise, structured revision notes for "
    "a student. Use headings and bullet points. Cover only what is present in "
    "the provided material - do not add outside facts. Keep it exam-focused."
)


@dataclass
class RevisionNotes:
    text: str
    sources: list[str]


def generate_revision_notes(llm: LLMAdapter, results: list[dict]) -> RevisionNotes:
    if not results:
        return RevisionNotes(text="No source material provided.", sources=[])

    context = "\n\n".join(f"({r['filename']} p.{r['page_number']}) {r['text']}" for r in results)
    prompt = f"Source material:\n\n{context}\n\nWrite concise structured revision notes."

    try:
        notes_text = llm.generate(prompt, system=REVISION_SYSTEM_PROMPT)
    except LLMUnavailableError as exc:
        notes_text = f"(LLM unavailable: {exc})"

    sources = sorted({f"{r['filename']} (p.{r['page_number']})" for r in results})
    return RevisionNotes(text=notes_text, sources=sources)
