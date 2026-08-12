"""IndexingService: chunk a document's pages, embed the chunks, persist both.

This is the glue between Task 5 (text processing), Task 6 (embeddings),
and Task 7 (search) - it is the only place that writes to both the
chunks table and the vector index, so the two never drift apart.
"""
from __future__ import annotations

from studymate.config.settings import Settings
from studymate.db import repositories as repo
from studymate.db.models import STATUS_FAILED, STATUS_INDEXED
from studymate.embeddings.service import EmbeddingModel, get_embedder
from studymate.search.index import VectorIndex
from studymate.text.chunker import chunk_text
from studymate.text.cleaner import clean_text
from studymate.utils.logging import get_logger

logger = get_logger(__name__)


class IndexingService:
    def __init__(self, settings: Settings, embedder: EmbeddingModel | None = None):
        self.settings = settings
        self.embedder = embedder or get_embedder(settings.embedding_model)
        self.index = VectorIndex.load_or_create(settings.vector_dir, self.embedder.dimension)

    def index_document(self, document_id: int) -> int:
        """Chunk + embed + index every page of a document. Returns chunk count."""
        db_path = self.settings.database_path
        pages = repo.list_pages(db_path, document_id)

        try:
            all_candidates = []
            for page in pages:
                cleaned = clean_text(page.extracted_text)
                candidates = chunk_text(
                    page.id, cleaned,
                    chunk_size=self.settings.chunk_size,
                    chunk_overlap=self.settings.chunk_overlap,
                )
                all_candidates.extend(candidates)

            if not all_candidates:
                repo.update_document_status(db_path, document_id, STATUS_INDEXED)
                return 0

            from studymate.db.models import Chunk
            chunk_rows = [Chunk(id=None, page_id=c.page_id, chunk_index=c.chunk_index, text=c.text)
                          for c in all_candidates]
            chunk_ids = repo.bulk_create_chunks(db_path, chunk_rows)

            texts = [c.text for c in all_candidates]
            vectors = self.embedder.embed(texts)
            self.index.add(vectors, chunk_ids)
            self.index.save(self.settings.vector_dir)

            repo.mark_chunks_embedded(db_path, chunk_ids)
            repo.update_document_status(db_path, document_id, STATUS_INDEXED)
            return len(chunk_ids)
        except Exception as exc:
            logger.exception("Indexing failed for document %s", document_id)
            repo.update_document_status(db_path, document_id, STATUS_FAILED, str(exc))
            return 0
