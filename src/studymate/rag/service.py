"""RAGService: retrieve -> build context -> generate -> attach sources.

Ties together rag/retriever.py, rag/prompt.py, and an LLMAdapter without
those layers knowing about each other, per skills.md Skill 8.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from studymate.ai.llm import LLMAdapter, LLMUnavailableError
from studymate.rag.prompt import RAG_SYSTEM_PROMPT, build_rag_prompt
from studymate.rag.retriever import has_sufficient_evidence, retrieve, top_raw_semantic_score
from studymate.search.service import SearchService


@dataclass
class RAGAnswer:
    question: str
    answer: str
    sources: list[dict] = field(default_factory=list)
    grounded: bool = True


NO_EVIDENCE_MESSAGE = (
    "I couldn't find relevant material in your uploaded documents to answer "
    "that question. Try rephrasing, or upload material that covers this topic."
)


class RAGService:
    def __init__(self, search_service: SearchService, llm: LLMAdapter):
        self.search_service = search_service
        self.llm = llm

    def ask(self, question: str, top_k: int | None = None) -> RAGAnswer:
        results = retrieve(self.search_service, question, top_k=top_k)
        raw_score = top_raw_semantic_score(self.search_service, question)

        if not results or not has_sufficient_evidence(raw_score):
            return RAGAnswer(question=question, answer=NO_EVIDENCE_MESSAGE, sources=[], grounded=False)

        prompt = build_rag_prompt(question, results)
        try:
            answer_text = self.llm.generate(prompt, system=RAG_SYSTEM_PROMPT)
        except LLMUnavailableError as exc:
            answer_text = f"{NO_EVIDENCE_MESSAGE}\n\n(LLM error: {exc})"
            return RAGAnswer(question=question, answer=answer_text, sources=results, grounded=False)

        return RAGAnswer(question=question, answer=answer_text, sources=results, grounded=True)
