"""Dashboard page: document/page/chunk counts, recent documents, status."""
from __future__ import annotations

import streamlit as st

from studymate.app_context import AppContext
from studymate.db import repositories as repo


def render(ctx: AppContext) -> None:
    st.header("Dashboard")

    counts = repo.counts(ctx.settings.database_path)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Documents", counts["documents"])
    col2.metric("Pages", counts["pages"])
    col3.metric("Chunks", counts["chunks"])
    col4.metric("Indexed", counts["indexed_documents"])

    st.subheader("Recent documents")
    documents = repo.list_documents(ctx.settings.database_path)[:10]
    if not documents:
        st.info("No documents uploaded yet. Go to the Upload page to get started.")
        return

    for doc in documents:
        status_icon = {
            "uploaded": "⏳", "processing": "⚙️", "processed": "✅",
            "indexed": "📚", "failed": "❌",
        }.get(doc.status, "•")
        with st.container(border=True):
            st.markdown(f"**{status_icon} {doc.filename}**  \n"
                        f"{doc.file_type.upper()} · {doc.pages} page(s) · status: `{doc.status}`")
            if doc.status == "failed" and doc.error_message:
                st.error(doc.error_message)
