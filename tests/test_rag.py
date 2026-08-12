"""Tests for the RAG pipeline (Task 8): retrieve -> ground -> attach sources,
and the no-evidence path that avoids fabricating answers. Uses a FakeLLM
so tests need no cloud service and no local model running.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from conftest_helpers import FakeLLM, make_test_settings

from studymate.db.database import init_db
from studymate.db import repositories as repo
from studymate.db.models import Chunk, Document, Page
from studymate.embeddings.service import HashingEmbedder
from studymate.rag.prompt import build_rag_prompt
from studymate.rag.retriever import has_sufficient_evidence
from studymate.rag.service import NO_EVIDENCE_MESSAGE, RAGService
from studymate.search.index import VectorIndex
from studymate.search.service import SearchService


class TestPromptBuilding(unittest.TestCase):
    def test_prompt_includes_numbered_sources(self):
        results = [
            {"filename": "a.pdf", "page_number": 1, "text": "Text A"},
            {"filename": "b.pdf", "page_number": 2, "text": "Text B"},
        ]
        prompt = build_rag_prompt("What is X?", results)
        self.assertIn("[Source 1]", prompt)
        self.assertIn("[Source 2]", prompt)
        self.assertIn("Text A", prompt)
        self.assertIn("What is X?", prompt)


class TestEvidenceGate(unittest.TestCase):
    def test_low_score_is_insufficient(self):
        self.assertFalse(has_sufficient_evidence(0.0))

    def test_reasonable_score_is_sufficient(self):
        self.assertTrue(has_sufficient_evidence(0.5))


class TestRAGService(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.settings = make_test_settings(Path(self.tmp.name))
        init_db(self.settings.database_path)
        db_path = self.settings.database_path

        doc_id = repo.create_document(db_path, Document(
            id=None, filename="db_notes.pdf", filepath="/tmp/db_notes.pdf",
            file_size=100, file_type="pdf", upload_date="2026-01-01",
        ))
        page_id = repo.create_page(db_path, Page(
            id=None, document_id=doc_id, page_number=3,
            extracted_text="A primary key uniquely identifies each row in a table.",
        ))
        chunk_id = repo.create_chunk(db_path, Chunk(
            id=None, page_id=page_id, chunk_index=0,
            text="A primary key uniquely identifies each row in a table.",
        ))

        self.embedder = HashingEmbedder(dimension=32)
        index = VectorIndex(dimension=32)
        vector = self.embedder.embed(["A primary key uniquely identifies each row in a table."])
        index.add(vector, chunk_ids=[chunk_id])
        index.save(self.settings.vector_dir)

        self.search_service = SearchService(self.settings, embedder=self.embedder)

    def test_grounded_answer_includes_sources(self):
        llm = FakeLLM(response="A primary key uniquely identifies rows. [Source 1]")
        rag = RAGService(self.search_service, llm)

        result = rag.ask("What is a primary key?")

        self.assertTrue(result.grounded)
        self.assertEqual(len(result.sources), 1)
        self.assertEqual(result.sources[0]["filename"], "db_notes.pdf")
        self.assertIn("primary key", result.answer.lower())
        self.assertEqual(len(llm.calls), 1)  # generation only happens once evidence is found

    def test_no_evidence_does_not_call_llm(self):
        llm = FakeLLM(response="should not be used")
        rag = RAGService(self.search_service, llm)

        result = rag.ask("What is the capital of France?")

        self.assertFalse(result.grounded)
        self.assertEqual(result.answer, NO_EVIDENCE_MESSAGE)
        self.assertEqual(llm.calls, [])  # never fabricates an answer without evidence


if __name__ == "__main__":
    unittest.main()
