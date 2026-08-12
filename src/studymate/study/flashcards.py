"""Flashcard generation. Every card carries question, answer, and source."""
from __future__ import annotations

from dataclasses import dataclass, field

from studymate.ai.llm import LLMAdapter, LLMUnavailableError
from studymate.study.common import safe_parse_json

FLASHCARD_SYSTEM_PROMPT = (
    "You are a study assistant generating flashcards from source material. "
    "Respond ONLY with a JSON array, no prose, no markdown fences. Each "
    "element must be an object with exactly these keys: \"question\", \"answer\". "
    "Base every card strictly on the given material."
)


@dataclass
class Flashcard:
    question: str
    answer: str
    source_document: str
    source_page: int


@dataclass
class FlashcardSet:
    cards: list[Flashcard] = field(default_factory=list)
    generation_error: str | None = None


def generate_flashcards(llm: LLMAdapter, results: list[dict], count: int = 8) -> FlashcardSet:
    if not results:
        return FlashcardSet(cards=[], generation_error="No source material provided.")

    context = "\n\n".join(f"({r['filename']} p.{r['page_number']}) {r['text']}" for r in results)
    prompt = f"Source material:\n\n{context}\n\nGenerate {count} flashcards as a JSON array."

    try:
        raw = llm.generate(prompt, system=FLASHCARD_SYSTEM_PROMPT)
    except LLMUnavailableError as exc:
        return FlashcardSet(cards=[], generation_error=str(exc))

    parsed = safe_parse_json(raw)
    if not isinstance(parsed, list):
        return FlashcardSet(cards=[], generation_error="Model output was not valid JSON.")

    # Round-robin assign source attribution across the retrieved chunks,
    # since the model's JSON output doesn't carry source metadata itself.
    cards = []
    for i, item in enumerate(parsed):
        if not isinstance(item, dict) or "question" not in item or "answer" not in item:
            continue
        source = results[i % len(results)]
        cards.append(Flashcard(
            question=str(item["question"]),
            answer=str(item["answer"]),
            source_document=source["filename"],
            source_page=source["page_number"],
        ))

    return FlashcardSet(cards=cards)
