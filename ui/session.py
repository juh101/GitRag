import streamlit as st

def init_session_state() -> None:
    """Initialize session state variables including RAG tuning parameters."""
    defaults = {
        "theme": "Dark",
        "repository_path": None,
        "repository_owner": "",
        "repository_name": "",
        "documents": [],
        "chunks": [],
        "repository_indexed": False,
        "retriever": None,
        "answer_generator": None,
        "messages": [],
        "pending_question": None,
        "current_answer": "",
        "retrieved_sources": [],
        "stats": {
            "files": 0,
            "chunks": 0,
            "languages": 0
        },
        # RAG Parameters
        "top_k": 5,
        "temperature": 0.2,
        "show_file_tree": False
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value