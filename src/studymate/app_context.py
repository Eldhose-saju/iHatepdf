"""Wires together settings + services into one object the UI can hold.

Streamlit reruns the whole script on every interaction, so this is built
once and cached (see ui usage with st.cache_resource) rather than
reconstructed per rerun.
"""
from __future__ import annotations

from dataclasses import dataclass

from studymate.ai.local import get_llm_adapter
from studymate.config.settings import Settings, get_settings
from studymate.db.database import init_db
from studymate.documents.manager import DocumentService
from studymate.rag.service import RAGService
from studymate.search.pipeline import IndexingService
from studymate.search.service import SearchService


@dataclass
class AppContext:
    settings: Settings
    document_service: DocumentService
    indexing_service: IndexingService
    search_service: SearchService
    rag_service: RAGService


def build_app_context() -> AppContext:
    settings = get_settings()
    init_db(settings.database_path)

    document_service = DocumentService(settings)
    indexing_service = IndexingService(settings)
    search_service = SearchService(settings, embedder=indexing_service.embedder)
    llm = get_llm_adapter(settings.llm_provider, settings.llm_model, settings.ollama_host)
    rag_service = RAGService(search_service, llm)

    return AppContext(
        settings=settings,
        document_service=document_service,
        indexing_service=indexing_service,
        search_service=search_service,
        rag_service=rag_service,
    )
