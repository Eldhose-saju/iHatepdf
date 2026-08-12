"""Study Tools page: Summarize / Flashcards / Quiz / Revision Notes."""
from __future__ import annotations

import streamlit as st

from studymate.app_context import AppContext
from studymate.db import database
from studymate.study.flashcards import generate_flashcards
from studymate.study.quizzes import generate_quiz
from studymate.study.revision import generate_revision_notes
from studymate.study.summaries import summarize_document


def render(ctx: AppContext) -> None:
    st.header("Study Tools")

    from studymate.db import repositories as repo
    documents = repo.list_documents(ctx.settings.database_path)
    indexed_docs = [d for d in documents if d.status == "indexed"]

    if not indexed_docs:
        st.info("Upload and index a document first (see the Upload page).")
        return

    doc_labels = {f"{d.filename} (#{d.id})": d for d in indexed_docs}
    selected_label = st.selectbox("Document", list(doc_labels.keys()))
    doc = doc_labels[selected_label]

    tab_summary, tab_flashcards, tab_quiz, tab_revision = st.tabs(
        ["Summarize", "Flashcards", "Quiz", "Revision Notes"]
    )

    with tab_summary:
        if st.button("Generate summary"):
            summary = summarize_document(ctx.settings, ctx.rag_service.llm, doc.id)
            st.write(summary.text)

    with tab_flashcards:
        count = st.slider("Number of flashcards", 3, 15, 8)
        if st.button("Generate flashcards"):
            results = ctx.search_service.search(doc.filename, mode="keyword", top_k=20) \
                or _document_context(ctx, doc.id)
            flashcard_set = generate_flashcards(ctx.rag_service.llm, results, count=count)
            if flashcard_set.generation_error:
                st.error(flashcard_set.generation_error)
            for card in flashcard_set.cards:
                with st.container(border=True):
                    st.markdown(f"**Q:** {card.question}")
                    st.markdown(f"**A:** {card.answer}")
                    st.caption(f"Source: {card.source_document}, page {card.source_page}")

    with tab_quiz:
        count = st.slider("Number of questions", 3, 10, 5)
        if st.button("Generate quiz"):
            results = _document_context(ctx, doc.id)
            quiz = generate_quiz(ctx.rag_service.llm, results, count=count)
            if quiz.generation_error:
                st.error(quiz.generation_error)
            for i, q in enumerate(quiz.questions, start=1):
                with st.container(border=True):
                    st.markdown(f"**{i}. {q.question}**")
                    for opt in q.options:
                        st.write(f"- {opt}")
                    with st.expander("Answer & explanation"):
                        st.write(f"Correct answer: {q.correct_answer}")
                        st.write(q.explanation)
                        st.caption(f"Source: {q.source_document}, page {q.source_page}")

    with tab_revision:
        if st.button("Generate revision notes"):
            results = _document_context(ctx, doc.id)
            notes = generate_revision_notes(ctx.rag_service.llm, results)
            st.write(notes.text)
            if notes.sources:
                st.caption("Sources: " + ", ".join(notes.sources))


def _document_context(ctx: AppContext, document_id: int, limit: int = 12) -> list[dict]:
    """Pull a document's own chunks directly as context for generation."""
    from studymate.db import repositories as repo

    pages = repo.list_pages(ctx.settings.database_path, document_id)
    doc = repo.get_document(ctx.settings.database_path, document_id)
    results = []
    for page in pages:
        db_path = ctx.settings.database_path
        with database.session(db_path) as conn:
            rows = conn.execute("SELECT id, text FROM chunks WHERE page_id = ?", (page.id,)).fetchall()
        for row in rows:
            results.append({
                "chunk_id": row["id"], "document_id": document_id, "filename": doc.filename,
                "page_number": page.page_number, "text": row["text"], "score": 1.0,
            })
        if len(results) >= limit:
            break
    return results[:limit]
