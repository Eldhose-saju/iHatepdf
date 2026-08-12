"""Search page: keyword / semantic / hybrid retrieval over indexed material."""
from __future__ import annotations

import streamlit as st

from studymate.app_context import AppContext


def render(ctx: AppContext) -> None:
    st.header("Search")

    query = st.text_input("Search your materials")
    mode = st.radio("Mode", ["hybrid", "keyword", "semantic"], horizontal=True)

    if not query:
        return

    results = ctx.search_service.search(query, mode=mode)
    if not results:
        st.info("No matching results. Try a different query or a different mode.")
        return

    for r in results:
        with st.container(border=True):
            st.markdown(f"**{r['filename']}** — page {r['page_number']} · score {r['score']:.3f}")
            st.write(r["text"][:600] + ("…" if len(r["text"]) > 600 else ""))
