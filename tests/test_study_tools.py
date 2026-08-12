"""Tests for summaries/flashcards/quizzes/revision notes (Tasks 9-12).

Uses FakeLLM so no cloud service or local model is required. Verifies
the required fields (source, question/answer, options/correct/explanation)
are present per skills.md Skill 10.
"""
from __future__ import annotations

import json
import unittest

from conftest_helpers import FakeLLM

from studymate.study.flashcards import generate_flashcards
from studymate.study.quizzes import generate_quiz
from studymate.study.revision import generate_revision_notes
from studymate.study.summaries import summarize_text

SAMPLE_RESULTS = [
    {"chunk_id": 1, "document_id": 1, "filename": "os.pdf", "page_number": 4,
     "text": "A deadlock requires mutual exclusion, hold and wait, no preemption, and circular wait.", "score": 0.9},
]


class TestSummaries(unittest.TestCase):
    def test_summary_carries_source_label(self):
        llm = FakeLLM(response="Deadlocks need four conditions to occur.")
        summary = summarize_text(llm, "some text", source_label="os.pdf")
        self.assertEqual(summary.source_label, "os.pdf")
        self.assertIn("Deadlocks", summary.text)


class TestFlashcards(unittest.TestCase):
    def test_generates_cards_with_source_attribution(self):
        llm = FakeLLM(response=json.dumps([
            {"question": "What is a deadlock?", "answer": "A cyclic resource-wait condition."},
        ]))
        result = generate_flashcards(llm, SAMPLE_RESULTS, count=1)
        self.assertIsNone(result.generation_error)
        self.assertEqual(len(result.cards), 1)
        card = result.cards[0]
        self.assertTrue(card.question)
        self.assertTrue(card.answer)
        self.assertEqual(card.source_document, "os.pdf")
        self.assertEqual(card.source_page, 4)

    def test_no_source_material_is_reported(self):
        result = generate_flashcards(FakeLLM(response="[]"), [], count=5)
        self.assertEqual(result.cards, [])
        self.assertIsNotNone(result.generation_error)

    def test_malformed_json_is_reported_not_raised(self):
        result = generate_flashcards(FakeLLM(response="not json"), SAMPLE_RESULTS, count=1)
        self.assertEqual(result.cards, [])
        self.assertIsNotNone(result.generation_error)


class TestQuizzes(unittest.TestCase):
    def test_generates_question_with_all_required_fields(self):
        llm = FakeLLM(response=json.dumps([{
            "question": "Which condition is NOT required for deadlock?",
            "options": ["Mutual exclusion", "Preemption", "Hold and wait", "Circular wait"],
            "correct_answer": "Preemption",
            "explanation": "Deadlock requires NO preemption, not preemption.",
        }]))
        quiz = generate_quiz(llm, SAMPLE_RESULTS, count=1)
        self.assertIsNone(quiz.generation_error)
        q = quiz.questions[0]
        self.assertEqual(len(q.options), 4)
        self.assertIn(q.correct_answer, q.options)
        self.assertTrue(q.explanation)
        self.assertEqual(q.source_document, "os.pdf")
        self.assertEqual(q.source_page, 4)

    def test_item_missing_required_key_is_skipped(self):
        llm = FakeLLM(response=json.dumps([{"question": "Incomplete?"}]))
        quiz = generate_quiz(llm, SAMPLE_RESULTS, count=1)
        self.assertEqual(quiz.questions, [])


class TestRevisionNotes(unittest.TestCase):
    def test_notes_list_sources(self):
        llm = FakeLLM(response="## Deadlocks\n- Four necessary conditions...")
        notes = generate_revision_notes(llm, SAMPLE_RESULTS)
        self.assertIn("Deadlocks", notes.text)
        self.assertIn("os.pdf (p.4)", notes.sources)

    def test_no_material_returns_message_without_calling_llm(self):
        llm = FakeLLM(response="should not be used")
        notes = generate_revision_notes(llm, [])
        self.assertEqual(notes.sources, [])
        self.assertEqual(llm.calls, [])


if __name__ == "__main__":
    unittest.main()
