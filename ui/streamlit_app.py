from pathlib import Path
import sys

# Setup Project Root Path Insertion
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

    # 1. State Setup
    init_session_state()

    # 2. Sidebar Setup & Theme Application
    render_sidebar()
    apply_theme(st.session_state.get("theme", "Dark"))

    # 3. Main Workspace Rendering
    render_header()
    render_repository()

    # 4. Split Column Layout (60% Chat / 40% Sources)
    col_chat, col_sources = st.columns([6, 4], gap="medium")

    with col_chat:
        render_chat()

    with col_sources:
        render_sources()

if __name__ == "__main__":
    main()