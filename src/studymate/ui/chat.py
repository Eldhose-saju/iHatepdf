"""AI Chat page: RAG question answering with source attribution."""
from __future__ import annotations

import streamlit as st

from studymate.app_context import AppContext


def render(ctx: AppContext) -> None:
    st.header("AI Chat")
    st.caption("Ask questions about your uploaded material. Answers are grounded in your documents.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for turn in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(turn["question"])
        with st.chat_message("assistant"):
            st.write(turn["answer"])
            if turn["sources"]:
                with st.expander("Sources"):
                    for s in turn["sources"]:
                        st.markdown(f"- {s['filename']}, page {s['page_number']} (score {s['score']:.3f})")

    question = st.chat_input("Ask a question about your materials...")
    if question:
        result = ctx.rag_service.ask(question)
        st.session_state.chat_history.append({
            "question": question, "answer": result.answer, "sources": result.sources,
        })
        st.rerun()
