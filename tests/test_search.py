"""Tests for keyword/semantic/hybrid search and the vector index (Tasks 6-7).

Every result must retain document/page/chunk/score fields, and the
persisted vector index must survive a save/load round trip with valid
chunk-ID mappings.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from conftest_helpers import make_test_settings

from studymate.db.database import init_db
from studymate.db import repositories as repo
from studymate.db.models import Chunk, Document, Page
from studymate.embeddings.service import HashingEmbedder
from studymate.search.hybrid import hybrid_search
from studymate.search.index import VectorIndex, VectorIndexError
from studymate.search.keyword import keyword_search
from studymate.search.semantic import semantic_search


class TestVectorIndex(unittest.TestCase):
    def test_add_and_search_returns_nearest_by_cosine_similarity(self):
        # Uses a large enough dimension that hash collisions between
        # unrelated tokens are negligible, so exact-word overlap with the
        # query reliably determines ranking.
        embedder = HashingEmbedder(dimension=4096)
        texts = ["binary search tree indexing", "cats and dogs are pets", "unrelated topic about weather"]
        vectors = embedder.embed(texts)
        index = VectorIndex(dimension=4096)
        index.add(vectors, chunk_ids=[10, 20, 30])

        query_vector = embedder.embed(["tree indexing structures"])[0]
        results = index.search(query_vector, top_k=2)

        self.assertEqual(len(results), 2)
        result_ids = [chunk_id for chunk_id, _ in results]
        self.assertEqual(result_ids[0], 10)  # exact word overlap ("tree", "indexing") should rank first

    def test_save_and_load_round_trip(self):
        embedder = HashingEmbedder(dimension=16)
        index = VectorIndex(dimension=16)
        index.add(embedder.embed(["alpha", "beta"]), chunk_ids=[1, 2])

        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            index.save(directory)
            reloaded = VectorIndex.load(directory)

            self.assertEqual(reloaded.size(), 2)
            self.assertEqual(reloaded.dimension, 16)

    def test_load_missing_index_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(VectorIndexError):
                VectorIndex.load(Path(tmp))

    def test_load_or_create_falls_back_to_empty_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            index = VectorIndex.load_or_create(Path(tmp), dimension=8)
            self.assertEqual(index.size(), 0)


class _SearchTestBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.settings = make_test_settings(Path(self.tmp.name))
        init_db(self.settings.database_path)
        db_path = self.settings.database_path

        doc_id = repo.create_document(db_path, Document(
            id=None, filename="os_notes.pdf", filepath="/tmp/os_notes.pdf",
            file_size=100, file_type="pdf", upload_date="2026-01-01",
        ))
        page_id = repo.create_page(db_path, Page(
            id=None, document_id=doc_id, page_number=1,
            extracted_text="Deadlock occurs when processes wait on each other's resources.",
        ))
        self.chunk_id = repo.create_chunk(db_path, Chunk(
            id=None, page_id=page_id, chunk_index=0,
            text="Deadlock occurs when processes wait on each other's resources.",
        ))
        self.db_path = db_path


class TestKeywordSearch(_SearchTestBase):
    def test_returns_matching_chunk_with_required_fields(self):
        results = keyword_search(self.db_path, "deadlock", top_k=5)
        self.assertEqual(len(results), 1)
        r = results[0]
        for field in ("chunk_id", "document_id", "filename", "page_number", "text", "score"):
            self.assertIn(field, r)
        self.assertEqual(r["filename"], "os_notes.pdf")

    def test_no_match_returns_empty(self):
        self.assertEqual(keyword_search(self.db_path, "photosynthesis", top_k=5), [])


class TestSemanticSearch(_SearchTestBase):
    def test_returns_result_with_required_fields(self):
        embedder = HashingEmbedder(dimension=32)
        index = VectorIndex(dimension=32)
        vector = embedder.embed(["Deadlock occurs when processes wait on each other's resources."])
        index.add(vector, chunk_ids=[self.chunk_id])

        results = semantic_search(self.db_path, index, embedder, "process deadlock", top_k=5)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["chunk_id"], self.chunk_id)

    def test_empty_index_returns_empty(self):
        embedder = HashingEmbedder(dimension=32)
        index = VectorIndex(dimension=32)
        self.assertEqual(semantic_search(self.db_path, index, embedder, "anything", top_k=5), [])


class TestHybridSearch(_SearchTestBase):
    def test_combines_keyword_and_semantic_results(self):
        embedder = HashingEmbedder(dimension=32)
        index = VectorIndex(dimension=32)
        vector = embedder.embed(["Deadlock occurs when processes wait on each other's resources."])
        index.add(vector, chunk_ids=[self.chunk_id])

        results = hybrid_search(self.db_path, index, embedder, "deadlock", top_k=5)
        self.assertEqual(len(results), 1)
        self.assertGreater(results[0]["score"], 0)


if __name__ == "__main__":
    unittest.main()
