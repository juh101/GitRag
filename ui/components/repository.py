import time
import streamlit as st
from scripts.index_repository import ingest_repository
from retrieval.vector_retriever import VectorRetriever
from llm.llm_client import LLMClient
from llm.prompt_builder import PromptBuilder
from llm.answer_generator import AnswerGenerator

def render_repository() -> None:
    st.markdown("""
        <div class="glass-card">
            <div class="card-header-title">📁 Repository Indexing</div>
            <div class="card-header-sub">Enter a public GitHub URL to clone, chunk, and index the codebase.</div>
        </div>
    """, unsafe_allow_html=True)

    col_input, col_btn = st.columns([4, 1], gap="small")
    
    with col_input:
        repo_url = st.text_input(
            "GitHub Repository URL",
            placeholder="https://github.com/pallets/markupsafe",
            label_visibility="collapsed"
        )
    with col_btn:
        index_clicked = st.button("⚡ Index Repo", use_container_width=True)

    if index_clicked:
        if not repo_url.strip():
            st.error("Please enter a valid GitHub repository URL.")
        else:
            try:
                # Interactive Pipeline Progress Timeline
                status_container = st.empty()
                
                with status_container.container():
                    st.info("🔄 Step 1/4: Cloning Repository from GitHub...")
                time.sleep(0.3)

                repo_path, docs, chunks = ingest_repository(repo_url)

                with status_container.container():
                    st.info(" Parsing AST & Generating Chunk Embeddings...")
                time.sleep(0.3)

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

                with status_container.container():
                    st.info("📦 Step 3/4: Building FAISS Vector Index...")
                time.sleep(0.3)

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

                with status_container.container():
                    st.success(f"✅ Step 4/4: Successfully Indexed {owner}/{repo_name}!")
                time.sleep(0.5)
                status_container.empty()
                st.rerun()

            except Exception as e:
                st.error(f"Indexing Error: {str(e)}")

    # Dashboard Metrics Row & File Tree Inspector
    if st.session_state.get("repository_indexed"):
        owner = st.session_state.get("repository_owner", "")
        repo = st.session_state.get("repository_name", "")
        stats = st.session_state.get("stats", {"files": 0, "chunks": 0, "languages": 0})

        st.markdown("<br>", unsafe_allow_html=True)
        r1, r2, r3, r4 = st.columns([3, 1.2, 1.2, 1.2], gap="medium")

        with r1:
            st.markdown(f"""
                <div class="repo-main-card">
                    <div class="repo-title-text">
                        <svg height="22" viewBox="0 0 16 16" width="22" fill="currentColor"><path d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z"></path></svg>
                        {owner} / {repo}
                        <span class="repo-badge-indexed">Indexed</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with r2:
            st.markdown(f"""
                <div class="metric-card-box">
                    <div class="metric-card-val">📄 {stats['files']}</div>
                    <div class="metric-card-lbl">Files</div>
                </div>
            """, unsafe_allow_html=True)

        with r3:
            st.markdown(f"""
                <div class="metric-card-box">
                    <div class="metric-card-val">📦 {stats['chunks']}</div>
                    <div class="metric-card-lbl">Chunks</div>
                </div>
            """, unsafe_allow_html=True)

        with r4:
            st.markdown(f"""
                <div class="metric-card-box">
                    <div class="metric-card-val">💻 {stats['languages']}</div>
                    <div class="metric-card-lbl">Languages</div>
                </div>
            """, unsafe_allow_html=True)

        # Interactive File Tree Drawer
        with st.expander("🌳 Inspect Parsed File Structure"):
            docs = st.session_state.get("documents", [])
            if docs:
                file_paths = [getattr(d, "file_path", f"File #{i}") for i, d in enumerate(docs)]
                for path in sorted(file_paths)[:15]:
                    st.text(f"📄 {path}")
                if len(file_paths) > 15:
                    st.caption(f"... and {len(file_paths) - 15} more files.")
            else:
                st.caption("No file details available.")