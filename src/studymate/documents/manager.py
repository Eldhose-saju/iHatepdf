"""DocumentService: orchestrates the upload -> parse -> OCR -> persist pipeline.

This is the only place that wires parsers, OCR, and the documents/pages
tables together, so Streamlit and other callers never touch that logic
directly (agent.md Section 11: UI rules).
"""
from __future__ import annotations

import shutil
from pathlib import Path

from studymate.config.settings import Settings
from studymate.db import repositories as repo
from studymate.db.models import Document, Page, STATUS_FAILED, STATUS_PROCESSED, STATUS_PROCESSING, STATUS_UPLOADED
from studymate.documents.metadata import file_type_of, now_iso
from studymate.documents.parsers.docx import DOCXParser
from studymate.documents.parsers.image import ImageParser
from studymate.documents.parsers.pdf import PDFParser
from studymate.documents.parsers.pptx import PPTXParser
from studymate.documents.validators import ValidationError, validate_upload
from studymate.ocr import service as ocr_service
from studymate.utils.files import is_image, unique_storage_name
from studymate.utils.logging import get_logger

logger = get_logger(__name__)

_PARSERS = {
    "pdf": PDFParser(),
    "docx": DOCXParser(),
    "pptx": PPTXParser(),
}


class DocumentService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def upload(self, source_path: Path, original_filename: str) -> Document:
        """Validate, store, record, and process a single uploaded file.

        Returns the resulting Document (status reflects success/failure;
        failures are recorded, never raised past this point, so batch
        uploads in the UI can continue with the next file).
        """
        file_size = source_path.stat().st_size

        try:
            validate_upload(original_filename, file_size, self.settings)
        except ValidationError:
            raise  # rejected before any DB/file-system side effects

        stored_name = unique_storage_name(original_filename)
        dest_path = self.settings.upload_dir / stored_name
        self.settings.upload_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, dest_path)

        doc = Document(
            id=None,
            filename=original_filename,
            filepath=str(dest_path),
            file_size=file_size,
            file_type=file_type_of(original_filename),
            upload_date=now_iso(),
            status=STATUS_UPLOADED,
        )
        document_id = repo.create_document(self.settings.database_path, doc)
        doc.id = document_id

        self._process(doc)
        return repo.get_document(self.settings.database_path, document_id)

    def _process(self, doc: Document) -> None:
        db_path = self.settings.database_path
        repo.update_document_status(db_path, doc.id, STATUS_PROCESSING)

        try:
            pages = self._extract_pages(doc)
        except Exception as exc:
            logger.exception("Extraction failed for document %s", doc.id)
            repo.update_document_status(db_path, doc.id, STATUS_FAILED, str(exc))
            return

        for page in pages:
            repo.create_page(db_path, page)

        repo.update_document_pages(db_path, doc.id, len(pages))
        repo.update_document_status(db_path, doc.id, STATUS_PROCESSED)

    def _extract_pages(self, doc: Document) -> list[Page]:
        filepath = Path(doc.filepath)

        if is_image(doc.filename):
            return [self._extract_image_page(doc, filepath)]

        parser = _PARSERS.get(doc.file_type)
        if parser is None:
            raise ValueError(f"No parser registered for file type '{doc.file_type}'.")

        parsed_pages = parser.parse(filepath)
        pages: list[Page] = []
        for parsed in parsed_pages:
            text = parsed.text
            ocr_used = False

            if self.settings.ocr_enabled and ocr_service.needs_ocr(text) and doc.file_type == "pdf":
                try:
                    ocr_text = ocr_service.ocr_pdf_page(filepath, parsed.page_number)
                    if ocr_text.strip():
                        text = ocr_text
                        ocr_used = True
                except ocr_service.OCRError as exc:
                    logger.warning("OCR skipped for %s page %s: %s", doc.filename, parsed.page_number, exc)

            pages.append(Page(
                id=None, document_id=doc.id, page_number=parsed.page_number,
                extracted_text=text, ocr_used=ocr_used,
            ))
        return pages

    def _extract_image_page(self, doc: Document, filepath: Path) -> Page:
        text = ""
        ocr_used = False
        if self.settings.ocr_enabled:
            try:
                text = ocr_service.ocr_image_file(filepath)
                ocr_used = True
            except ocr_service.OCRError as exc:
                logger.warning("OCR failed for image %s: %s", doc.filename, exc)
        return Page(id=None, document_id=doc.id, page_number=1, extracted_text=text, ocr_used=ocr_used)
