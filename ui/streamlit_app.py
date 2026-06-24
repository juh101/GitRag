import streamlit as st

from chunking.code_chunker import chunk_documents
from ingest.clone_repo import clone_repository
from ingest.parse_repo import parse_repository

def apply_theme(theme: str) -> None:
    """
    Apply basic light or dark theme using custom CSS.
    """
    if theme == "Dark":
        background_color = "#0E1117"
        text_color = "#FAFAFA"
        card_color = "#1E1E1E"
        border_color = "#333333"
    else:
        background_color = "#FFFFFF"
        text_color = "#111111"
        card_color = "#F5F5F5"
        border_color = "#DDDDDD"

    st.markdown(
        f"""
        <style>
            .stApp {{
                background-color: {background_color};
                color: {text_color};
            }}

            .main-card {{
                background-color: {card_color};
                border: 1px solid {border_color};
                border-radius: 12px;
                padding: 18px;
                margin-bottom: 16px;
            }}

            .section-title {{
                font-size: 22px;
                font-weight: 700;
                margin-bottom: 8px;
            }}

            .small-muted {{
                font-size: 14px;
                opacity: 0.75;
            }}

            .metric-card {{
                background-color: {card_color};
                border: 1px solid {border_color};
                border-radius: 10px;
                padding: 14px;
                text-align: center;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def initialize_session_state() -> None:
    """
    Store app-level state so results remain visible after button clicks.
    """
    if "repository_path" not in st.session_state:
        st.session_state.repository_path = None

    if "documents" not in st.session_state:
        st.session_state.documents = []

    if "chunks" not in st.session_state:
        st.session_state.chunks = []


def render_header() -> None:
    st.title("GitHub Repository RAG")
    st.caption(
        "A basic interface for cloning repositories, parsing files, chunking code, "
        "and preparing for future semantic search and LLM-based code Q&A."
    )


def render_sidebar() -> str:
    st.sidebar.title("Settings")

    theme = st.sidebar.radio(
        "Theme",
        options=["Light", "Dark"],
        index=0,
    )

    st.sidebar.divider()

    st.sidebar.subheader("Current Features")
    st.sidebar.write("✅ Clone GitHub repository")
    st.sidebar.write("✅ Parse useful source files")
    st.sidebar.write("✅ Filter junk folders/files")
    st.sidebar.write("✅ Chunk code with line numbers")

    st.sidebar.subheader("Upcoming Features")
    st.sidebar.write("🔜 Generate embeddings")
    st.sidebar.write("🔜 Build FAISS index")
    st.sidebar.write("🔜 Save/load metadata")
    st.sidebar.write("🔜 Ask questions about repo")
    st.sidebar.write("🔜 LLM answer with citations")

    return theme


def render_repository_indexing_section() -> None:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">1. Repository Indexing</div>',
        unsafe_allow_html=True,
    )

    repo_url = st.text_input(
        "Enter GitHub Repository URL",
        placeholder="https://github.com/pallets/markupsafe.git",
    )

    index_button = st.button("Clone, Parse, and Chunk Repository")

    if index_button:
        if not repo_url.strip():
            st.error("Please enter a valid GitHub repository URL.")
        else:
            try:
                with st.spinner("Cloning or locating repository..."):
                    repository_path = clone_repository(repo_url)

                with st.spinner("Parsing repository files..."):
                    documents = parse_repository(repository_path)

                with st.spinner("Chunking parsed files..."):
                    chunks = chunk_documents(documents)

                st.session_state.repository_path = repository_path
                st.session_state.documents = documents
                st.session_state.chunks = chunks

                st.success("Repository processed successfully.")

            except Exception as error:
                st.error(f"Something went wrong: {error}")

    st.markdown("</div>", unsafe_allow_html=True)


def render_stats_section() -> None:
    documents = st.session_state.documents
    chunks = st.session_state.chunks
    repository_path = st.session_state.repository_path

    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">2. Current Repository Status</div>',
        unsafe_allow_html=True,
    )

    if repository_path:
        st.write(f"**Repository Path:** `{repository_path}`")
    else:
        st.write("No repository processed yet.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Parsed Files", len(documents))

    with col2:
        st.metric("Code Chunks", len(chunks))

    with col3:
        languages = {document.language for document in documents}
        st.metric("Languages Found", len(languages))

    st.markdown("</div>", unsafe_allow_html=True)


def render_documents_section() -> None:
    documents = st.session_state.documents

    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">3. Parsed Files</div>',
        unsafe_allow_html=True,
    )

    if not documents:
        st.info("Parsed files will appear here after repository processing.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    max_files_to_show = st.slider(
        "Number of files to show",
        min_value=5,
        max_value=min(100, len(documents)),
        value=min(10, len(documents)),
    )

    for document in documents[:max_files_to_show]:
        with st.expander(
            f"{document.file_path} | {document.language} | {document.size_bytes} bytes"
        ):
            st.code(
                document.content[:3000],
                language=document.language if document.language != "unknown" else None,
            )

            if len(document.content) > 3000:
                st.caption("Showing first 3000 characters only.")

    st.markdown("</div>", unsafe_allow_html=True)


def render_chunks_section() -> None:
    chunks = st.session_state.chunks

    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">4. Code Chunks</div>',
        unsafe_allow_html=True,
    )

    if not chunks:
        st.info("Code chunks will appear here after repository processing.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    max_chunks_to_show = st.slider(
        "Number of chunks to show",
        min_value=5,
        max_value=min(100, len(chunks)),
        value=min(10, len(chunks)),
    )

    for chunk in chunks[:max_chunks_to_show]:
        with st.expander(
            f"{chunk.file_path} | lines {chunk.start_line}-{chunk.end_line} | chunk {chunk.chunk_index}"
        ):
            st.code(
                chunk.content,
                language=chunk.language if chunk.language != "unknown" else None,
            )

    st.markdown("</div>", unsafe_allow_html=True)


def render_future_query_section() -> None:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">5. Ask Questions About Repository</div>',
        unsafe_allow_html=True,
    )

    question = st.text_input(
        "Ask a question",
        placeholder="Where is authentication implemented?",
    )

    st.button(
        "Search Repository",
        disabled=True,
        help="This will be enabled after FAISS retrieval and LLM answer generation are added.",
    )

    st.info(
        "Coming soon: this section will embed your question, search the FAISS index, "
        "retrieve relevant chunks, and generate an answer with citations."
    )

    if question:
        st.caption(
            "Question captured. Retrieval is not connected yet."
        )

    st.markdown("</div>", unsafe_allow_html=True)


def render_future_features_section() -> None:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">6. Future Features Roadmap</div>',
        unsafe_allow_html=True,
    )

    st.checkbox("Embeddings generated for chunks", value=False, disabled=True)
    st.checkbox("FAISS index created", value=False, disabled=True)
    st.checkbox("Metadata saved", value=False, disabled=True)
    st.checkbox("Question retrieval enabled", value=False, disabled=True)
    st.checkbox("LLM answer generation enabled", value=False, disabled=True)
    st.checkbox("Repository architecture summary", value=False, disabled=True)
    st.checkbox("Function/class-level code-aware retrieval", value=False, disabled=True)

    st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(
        page_title="GitHub Repository RAG",
        page_icon="🔎",
        layout="wide",
    )

    initialize_session_state()

    theme = render_sidebar()
    apply_theme(theme)

    render_header()
    render_repository_indexing_section()
    render_stats_section()
    render_documents_section()
    render_chunks_section()
    render_future_query_section()
    render_future_features_section()


if __name__ == "__main__":
    main()