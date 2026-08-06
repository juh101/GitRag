from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from ui.session import init_session_state
from ui.styles import apply_theme
from ui.components.sidebar import render_sidebar
from ui.components.header import render_header
from ui.components.repository import render_repository
from ui.components.chat import render_chat
from ui.components.sources import render_sources

def main() -> None:
    st.set_page_config(
        page_title="GitHub Repository AI Assistant",
        page_icon="✨",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    init_session_state()

    # 1. Render Sidebar to pick up state interactions
    render_sidebar()

    # 2. Apply theme according to session state
    apply_theme(st.session_state.get("theme", "Dark"))

    # 3. Main Dashboard Layout
    render_header()
    render_repository()

    st.markdown("<br>", unsafe_allow_html=True)

    col_chat, col_sources = st.columns([6, 4], gap="large")

    with col_chat:
        render_chat()

    with col_sources:
        render_sources()

if __name__ == "__main__":
    main()