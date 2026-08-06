import streamlit as st

def render_sidebar() -> None:
    st.sidebar.markdown(
        "### 🐙 GitHub Repository\n**AI Assistant**\n\n"
        "Understand any repository using Retrieval-Augmented Generation"
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Theme**")

    current_theme = st.session_state.get("theme", "Dark")
    selected_theme = st.sidebar.radio(
        "Select Theme",
        options=["Dark", "Light"],
        index=0 if current_theme == "Dark" else 1,
        key="theme_radio_input",
        label_visibility="collapsed"
    )

    if selected_theme != current_theme:
        st.session_state.theme = selected_theme
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("**⚙️ RAG Hyper-Parameters**")

    # Interactive Model Controls
    st.session_state.top_k = st.sidebar.slider(
        "Top-K Chunks Retrieved",
        min_value=1,
        max_value=10,
        value=st.session_state.get("top_k", 5),
        step=1,
        help="Number of relevant code chunks passed to the LLM context window."
    )

    st.session_state.temperature = st.sidebar.slider(
        "Gemini Temperature",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.get("temperature", 0.2),
        step=0.1,
        help="Lower values produce deterministic answers; higher values produce creative explanations."
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Repository Status**")

    if st.session_state.get("repository_indexed"):
        owner = st.session_state.get("repository_owner", "N/A")
        repo = st.session_state.get("repository_name", "N/A")
        st.sidebar.success(f"Indexed: **{owner}/{repo}**")
    else:
        st.sidebar.info("No repository indexed yet.")

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Quick Actions**")
    
    if st.sidebar.button("🗑️ Clear Conversation", key="sidebar_clear_btn", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_answer = ""
        st.session_state.retrieved_sources = []
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "GitHub Repository AI Assistant uses semantic search with FAISS "
        "and Gemini to answer repository-specific questions."
    )