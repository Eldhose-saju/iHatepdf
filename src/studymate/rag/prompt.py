"""Prompt construction, kept separate from retrieval and LLM invocation."""
from __future__ import annotations

RAG_SYSTEM_PROMPT = (
    "You are a study assistant. Answer the student's question using ONLY the "
    "provided source excerpts. If the excerpts do not contain enough "
    "information to answer, say so plainly instead of guessing. Cite sources "
    "using the [Source N] markers already present in the context."
)


def build_context(results: list[dict]) -> str:
    parts = []
    for i, r in enumerate(results, start=1):
        parts.append(
            f"[Source {i}] ({r['filename']}, page {r['page_number']})\n{r['text']}"
        )
    return "\n\n".join(parts)


def build_rag_prompt(question: str, results: list[dict]) -> str:
    context = build_context(results)
    return (
        f"Source excerpts:\n{context}\n\n"
        f"Question: {question}\n\n"
        f"Answer the question using only the excerpts above, and reference "
        f"which [Source N] each part of your answer comes from."
    )
