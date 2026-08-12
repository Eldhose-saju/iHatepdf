"""StudyMate AI - Streamlit entry point.

Run with: streamlit run app.py

This file only wires navigation to page render functions - all real
logic lives in src/studymate/* services (agent.md Section 11: UI rules).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import streamlit as st

from studymate.app_context import build_app_context
from studymate.ui import chat, dashboard, search, study_tools, upload

st.set_page_config(page_title="StudyMate AI", page_icon="📚", layout="wide")


@st.cache_resource
def get_context():
    return build_app_context()


def main() -> None:
    ctx = get_context()

    st.sidebar.title("📚 StudyMate AI")
    page = st.sidebar.radio(
        "Navigate",
        ["Dashboard", "Upload", "Search", "AI Chat", "Study Tools"],
    )

    if page == "Dashboard":
        dashboard.render(ctx)
    elif page == "Upload":
        upload.render(ctx)
    elif page == "Search":
        search.render(ctx)
    elif page == "AI Chat":
        chat.render(ctx)
    elif page == "Study Tools":
        study_tools.render(ctx)


if __name__ == "__main__":
    main()
