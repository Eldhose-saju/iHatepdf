"""Tests for document upload/validation/persistence (Task 2)."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from conftest_helpers import make_test_settings

from studymate.db.database import init_db
from studymate.db import repositories as repo
from studymate.documents.manager import DocumentService
from studymate.documents.validators import ValidationError, validate_upload


class TestValidation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.settings = make_test_settings(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def test_rejects_unsupported_extension(self):
        with self.assertRaises(ValidationError):
            validate_upload("notes.exe", 1000, self.settings)

    def test_rejects_empty_file(self):
        with self.assertRaises(ValidationError):
            validate_upload("notes.pdf", 0, self.settings)

    def test_rejects_oversized_file(self):
        too_big = (self.settings.max_upload_mb + 1) * 1024 * 1024
        with self.assertRaises(ValidationError):
            validate_upload("notes.pdf", too_big, self.settings)

    def test_accepts_valid_pdf(self):
        validate_upload("notes.pdf", 1000, self.settings)  # should not raise


class TestDocumentUpload(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.settings = make_test_settings(Path(self.tmp.name))
        init_db(self.settings.database_path)
        self.service = DocumentService(self.settings)

    def tearDown(self):
        self.tmp.cleanup()

    def test_upload_creates_document_record_and_stored_file(self):
        src = Path(self.tmp.name) / "source.docx"
        import docx
        d = docx.Document()
        d.add_paragraph("Operating systems manage processes and memory.")
        d.save(str(src))

        doc = self.service.upload(src, "source.docx")

        self.assertIsNotNone(doc.id)
        self.assertEqual(doc.status, "processed")
        self.assertTrue(Path(doc.filepath).exists())

        fetched = repo.get_document(self.settings.database_path, doc.id)
        self.assertEqual(fetched.filename, "source.docx")

        pages = repo.list_pages(self.settings.database_path, doc.id)
        self.assertEqual(len(pages), 1)
        self.assertIn("Operating systems", pages[0].extracted_text)

    def test_unsupported_file_is_rejected_cleanly(self):
        src = Path(self.tmp.name) / "bad.exe"
        src.write_bytes(b"not a real document")
        with self.assertRaises(ValidationError):
            self.service.upload(src, "bad.exe")


if __name__ == "__main__":
    unittest.main()
