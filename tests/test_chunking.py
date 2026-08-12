"""Tests for text cleaning and chunking (Task 5): no empty chunks,
deterministic output, source/page traceability preserved via page_id.
"""
from __future__ import annotations

import unittest

from conftest_helpers import ROOT as PROJECT_ROOT  # noqa: F401

from studymate.text.chunker import chunk_text
from studymate.text.cleaner import clean_text


class TestCleaner(unittest.TestCase):
    def test_collapses_whitespace_and_blank_lines(self):
        raw = "Hello   world\n\n\n\nSecond   line"
        cleaned = clean_text(raw)
        self.assertNotIn("   ", cleaned)
        self.assertNotIn("\n\n\n", cleaned)

    def test_joins_hyphenated_linebreak_words(self):
        raw = "This is informa-\ntion about databases."
        self.assertIn("information", clean_text(raw))

    def test_empty_input_returns_empty_string(self):
        self.assertEqual(clean_text(""), "")
        self.assertEqual(clean_text("   \n  "), "")


class TestChunker(unittest.TestCase):
    def test_no_empty_chunks(self):
        text = "word " * 500
        chunks = chunk_text(page_id=1, text=text, chunk_size=100, chunk_overlap=20)
        self.assertTrue(all(c.text.strip() for c in chunks))

    def test_empty_text_produces_no_chunks(self):
        self.assertEqual(chunk_text(page_id=1, text="", chunk_size=100, chunk_overlap=20), [])

    def test_deterministic_output(self):
        text = "The quick brown fox jumps over the lazy dog. " * 20
        first = chunk_text(page_id=1, text=text, chunk_size=100, chunk_overlap=20)
        second = chunk_text(page_id=1, text=text, chunk_size=100, chunk_overlap=20)
        self.assertEqual([c.text for c in first], [c.text for c in second])

    def test_page_id_traceability(self):
        chunks = chunk_text(page_id=42, text="a " * 300, chunk_size=100, chunk_overlap=20)
        self.assertTrue(all(c.page_id == 42 for c in chunks))

    def test_chunk_indices_are_sequential(self):
        chunks = chunk_text(page_id=1, text="a " * 300, chunk_size=100, chunk_overlap=20)
        self.assertEqual([c.chunk_index for c in chunks], list(range(len(chunks))))

    def test_rejects_overlap_not_smaller_than_size(self):
        with self.assertRaises(ValueError):
            chunk_text(page_id=1, text="hello world", chunk_size=50, chunk_overlap=50)


if __name__ == "__main__":
    unittest.main()
