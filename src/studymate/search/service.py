"""SearchService: the single entry point the UI/RAG layer calls for retrieval."""
from __future__ import annotations

from studymate.config.settings import Settings
from studymate.embeddings.service import EmbeddingModel, get_embedder
from studymate.search.hybrid import hybrid_search
from studymate.search.index import VectorIndex
from studymate.search.keyword import keyword_search
from studymate.search.semantic import semantic_search


class SearchService:
    def __init__(self, settings: Settings, embedder: EmbeddingModel | None = None):
        self.settings = settings
        self.embedder = embedder or get_embedder(settings.embedding_model)
        self.index = VectorIndex.load_or_create(settings.vector_dir, self.embedder.dimension)

    def reload_index(self) -> None:
        """Pick up an index that was updated (e.g. by a fresh upload) since init."""
        self.index = VectorIndex.load_or_create(self.settings.vector_dir, self.embedder.dimension)

    def search(self, query: str, mode: str = "hybrid", top_k: int | None = None) -> list[dict]:
        top_k = top_k or self.settings.top_k
        db_path = self.settings.database_path

        if mode == "keyword":
            return keyword_search(db_path, query, top_k=top_k)
        if mode == "semantic":
            return semantic_search(db_path, self.index, self.embedder, query, top_k=top_k)
        if mode == "hybrid":
            return hybrid_search(db_path, self.index, self.embedder, query, top_k=top_k)
        raise ValueError(f"Unknown search mode '{mode}'. Use keyword, semantic, or hybrid.")
