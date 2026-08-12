"""Upload page: file upload UI + validation + processing kickoff."""
from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

from studymate.app_context import AppContext
from studymate.documents.validators import ValidationError


def render(ctx: AppContext) -> None:
    st.header("Upload material")
    st.caption("Supported: PDF, DOCX, PPTX, and common image formats.")

    uploaded_files = st.file_uploader(
        "Choose file(s)", accept_multiple_files=True,
        type=["pdf", "docx", "pptx", "png", "jpg", "jpeg", "tif", "tiff", "bmp"],
    )

    if uploaded_files and st.button("Process uploads", type="primary"):
        for uploaded in uploaded_files:
            with st.status(f"Processing {uploaded.name}...", expanded=False) as status:
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded.name).suffix) as tmp:
                        tmp.write(uploaded.getbuffer())
                        tmp_path = Path(tmp.name)

                    doc = ctx.document_service.upload(tmp_path, uploaded.name)
                    tmp_path.unlink(missing_ok=True)

                    if doc.status == "failed":
                        status.update(label=f"{uploaded.name}: failed", state="error")
                        st.error(doc.error_message)
                        continue

                    chunk_count = ctx.indexing_service.index_document(doc.id)
                    ctx.search_service.reload_index()
                    status.update(label=f"{uploaded.name}: indexed ({doc.pages} pages, {chunk_count} chunks)",
                                  state="complete")
                except ValidationError as exc:
                    status.update(label=f"{uploaded.name}: rejected", state="error")
                    st.error(str(exc))
        st.success("Done. See the Dashboard for current status.")
