import streamlit as st
from scripts.index_repository import ingest_repository
from retrieval.vector_retriever import VectorRetriever
from llm.llm_client import LLMClient
from llm.prompt_builder import PromptBuilder
from llm.answer_generator import AnswerGenerator

def render_repository() -> None:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    st.markdown("#### 📁 Repository")
    st.caption("A GitHub repository is indexed and ready for questions.")
    
    col_input, col_btn = st.columns([4, 1], gap="small")
    
    with col_input:
        repo_url = st.text_input(
            "GitHub Repository URL",
            placeholder="https://github.com/pallets/flask",
            label_visibility="collapsed"
        )
    with col_btn:
        index_clicked = st.button("⚡ Index Repo", use_container_width=True)

    if index_clicked:
        if not repo_url.strip():
            st.error("Please enter a valid GitHub repository URL.")
        else:
            try:
                with st.spinner("Cloning, parsing, and building vector index..."):
                    repo_path, docs, chunks = ingest_repository(repo_url)

                    # Extract owner & repo from URL
                    clean_url = repo_url.rstrip("/").removesuffix(".git")
                    parts = clean_url.split("/")
                    owner = parts[-2] if len(parts) >= 2 else "owner"
                    repo_name = parts[-1] if len(parts) >= 1 else "repo"

                    retriever = VectorRetriever(repo_path)
                    prompt_builder = PromptBuilder()
                    llm_client = LLMClient()
                    answer_generator = AnswerGenerator(
                        retriever,
                        prompt_builder,
                        llm_client,
                    )

                    languages = {
                        getattr(doc, "language", "unknown") for doc in docs
                    }

                    st.session_state.repository_path = repo_path
                    st.session_state.repository_owner = owner
                    st.session_state.repository_name = repo_name
                    st.session_state.documents = docs
                    st.session_state.chunks = chunks
                    st.session_state.answer_generator = answer_generator
                    st.session_state.repository_indexed = True
                    st.session_state.stats = {
                        "files": len(docs),
                        "chunks": len(chunks),
                        "languages": len(languages)
                    }
                    st.rerun()
            except Exception as e:
                st.error(f"Indexing Failed: {str(e)}")

    # Display Metrics Row if Repository Indexed
    if st.session_state.get("repository_indexed"):
        owner = st.session_state.get("repository_owner", "pallets")
        repo = st.session_state.get("repository_name", "flask")
        stats = st.session_state.get("stats", {"files": 0, "chunks": 0, "languages": 0})

        st.markdown("<br>", unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns([2.5, 1.5, 1.5, 1.5], gap="small")

        with m1:
            st.markdown(f"""
                <div class="metric-box">
                    <span class="metric-icon">🐙</span>
                    <div>
                        <div class="metric-val">{owner} / {repo} <span class="status-badge-green">Indexed</span></div>
                        <div class="metric-lbl">Target Repository</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with m2:
            st.markdown(f"""
                <div class="metric-box">
                    <span class="metric-icon">📄</span>
                    <div>
                        <div class="metric-val">{stats['files']}</div>
                        <div class="metric-lbl">Files</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with m3:
            st.markdown(f"""
                <div class="metric-box">
                    <span class="metric-icon">📦</span>
                    <div>
                        <div class="metric-val">{stats['chunks']}</div>
                        <div class="metric-lbl">Chunks</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with m4:
            st.markdown(f"""
                <div class="metric-box">
                    <span class="metric-icon">💻</span>
                    <div>
                        <div class="metric-val">{stats['languages']}</div>
                        <div class="metric-lbl">Languages</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)