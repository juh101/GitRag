import streamlit as st


def initialize_session_state() -> None:
    """
    Initialize all session state variables used across the app.
    """

    defaults = {
        "pending_question": None,
        "repository_path": None,
        "repository_name": "",
        "repository_owner": "",
        "documents": [],
        "chunks": [],
        "answer_generator": None,
        "retriever": None,
        "messages": [],
        "current_answer": "",
        "retrieved_sources": [],
        "repository_indexed": False,
        "is_processing": False,
        "stats": {
            "files": 0,
            "chunks": 0,
            "languages": 0,
        },
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value