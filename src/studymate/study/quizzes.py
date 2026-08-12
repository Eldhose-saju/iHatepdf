"""Multiple-choice quiz generation with answers, explanations, and sources."""
from __future__ import annotations

from dataclasses import dataclass, field

from studymate.ai.llm import LLMAdapter, LLMUnavailableError
from studymate.study.common import safe_parse_json

QUIZ_SYSTEM_PROMPT = (
    "You are a study assistant generating a multiple-choice quiz from source "
    "material. Respond ONLY with a JSON array, no prose, no markdown fences. "
    "Each element must be an object with exactly these keys: \"question\", "
    "\"options\" (array of 4 strings), \"correct_answer\" (must exactly match "
    "one option string), \"explanation\". Base every question strictly on the "
    "given material."
)


@dataclass
class QuizQuestion:
    question: str
    options: list[str]
    correct_answer: str
    explanation: str
    source_document: str
    source_page: int


@dataclass
class Quiz:
    questions: list[QuizQuestion] = field(default_factory=list)
    generation_error: str | None = None


def generate_quiz(llm: LLMAdapter, results: list[dict], count: int = 5) -> Quiz:
    if not results:
        return Quiz(questions=[], generation_error="No source material provided.")

    context = "\n\n".join(f"({r['filename']} p.{r['page_number']}) {r['text']}" for r in results)
    prompt = f"Source material:\n\n{context}\n\nGenerate {count} multiple-choice questions as a JSON array."

    try:
        raw = llm.generate(prompt, system=QUIZ_SYSTEM_PROMPT)
    except LLMUnavailableError as exc:
        return Quiz(questions=[], generation_error=str(exc))

    parsed = safe_parse_json(raw)
    if not isinstance(parsed, list):
        return Quiz(questions=[], generation_error="Model output was not valid JSON.")

    questions = []
    required_keys = {"question", "options", "correct_answer", "explanation"}
    for i, item in enumerate(parsed):
        if not isinstance(item, dict) or not required_keys.issubset(item.keys()):
            continue
        if not isinstance(item["options"], list) or len(item["options"]) < 2:
            continue
        source = results[i % len(results)]
        questions.append(QuizQuestion(
            question=str(item["question"]),
            options=[str(o) for o in item["options"]],
            correct_answer=str(item["correct_answer"]),
            explanation=str(item["explanation"]),
            source_document=source["filename"],
            source_page=source["page_number"],
        ))

    return Quiz(questions=questions)
