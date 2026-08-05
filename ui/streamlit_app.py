from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from llm.answer_generator import AnswerGenerator
from llm.llm_client import LLMClient
from llm.prompt_builder import PromptBuilder
from retrieval.vector_retriever import VectorRetriever
from scripts.index_repository import ingest_repository


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
    Store app-level state.
    """

    defaults = {
        "repository_path": None,
        "documents": [],
        "chunks": [],
        "answer_generator": None,
        "current_answer": "",
        "retrieved_sources": [],
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

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

    st.sidebar.subheader("Pipeline")

    st.sidebar.write("✅ Clone Repository")
    st.sidebar.write("✅ Parse Repository")
    st.sidebar.write("✅ Chunk Code")
    st.sidebar.write("✅ Generate Embeddings")
    st.sidebar.write("✅ Build FAISS Index")
    st.sidebar.write("✅ Save Metadata")
    st.sidebar.write("✅ Semantic Retrieval")
    st.sidebar.write("✅ Prompt Builder")
    st.sidebar.write("✅ Gemini Integration")

    if st.session_state.answer_generator is not None:
        st.sidebar.success("Repository Ready")
    else:
        st.sidebar.warning("No Repository Loaded")

    return theme


def render_repository_indexing_section() -> None:

    st.markdown('<div class="main-card">', unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">1. Repository Indexing</div>',
        unsafe_allow_html=True,
    )

    repo_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/pallets/markupsafe.git",
    )

    if st.button("Index Repository"):

        if not repo_url.strip():
            st.error("Please enter a repository URL.")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        try:

            with st.spinner("Indexing repository..."):

                (
                    repository_path,
                    documents,
                    chunks,
                ) = ingest_repository(repo_url)

            retriever = VectorRetriever(repository_path)

            prompt_builder = PromptBuilder()

            llm_client = LLMClient()

            answer_generator = AnswerGenerator(
                retriever,
                prompt_builder,
                llm_client,
            )

            st.session_state.repository_path = repository_path
            st.session_state.documents = documents
            st.session_state.chunks = chunks
            st.session_state.answer_generator = answer_generator
            st.session_state.current_answer = ""
            st.session_state.retrieved_sources = []

            st.success("Repository indexed successfully.")

        except Exception as error:

            st.error(str(error))

    st.markdown("</div>", unsafe_allow_html=True)
    

def render_stats_section() -> None:

    documents = st.session_state.documents
    chunks = st.session_state.chunks
    repository_path = st.session_state.repository_path

    st.markdown('<div class="main-card">', unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">2. Repository Status</div>',
        unsafe_allow_html=True,
    )

    if repository_path is None:

        st.info("No repository indexed yet.")

        st.markdown("</div>", unsafe_allow_html=True)
        return

    owner = repository_path.parent.name
    repository = repository_path.name

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Repository",
        repository,
    )

    col2.metric(
        "Files",
        len(documents),
    )

    col3.metric(
        "Chunks",
        len(chunks),
    )

    languages = {
        document.language
        for document in documents
    }

    col4.metric(
        "Languages",
        len(languages),
    )

    st.caption(f"Repository Path: {repository_path}")

    st.markdown("</div>", unsafe_allow_html=True)


def render_documents_section() -> None:

    documents = st.session_state.documents

    st.markdown('<div class="main-card">', unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">3. Parsed Files</div>',
        unsafe_allow_html=True,
    )

    if not documents:

        st.info("Index a repository first.")

        st.markdown("</div>", unsafe_allow_html=True)
        return

    files_to_show = st.slider(
        "Files",
        1,
        len(documents),
        min(10, len(documents)),
    )

    for document in documents[:files_to_show]:

        with st.expander(document.file_path):

            st.write(f"Language: **{document.language}**")

            st.write(f"Size: **{document.size_bytes} bytes**")

            st.code(
                document.content[:3000],
                language=(
                    document.language
                    if document.language != "unknown"
                    else None
                ),
            )

            if len(document.content) > 3000:

                st.caption("Showing first 3000 characters.")

    st.markdown("</div>", unsafe_allow_html=True)
    

def render_chunks_section() -> None:

    chunks = st.session_state.chunks

    st.markdown('<div class="main-card">', unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">4. Code Chunks</div>',
        unsafe_allow_html=True,
    )

    if not chunks:

        st.info("Index a repository first.")

        st.markdown("</div>", unsafe_allow_html=True)
        return

    chunks_to_show = st.slider(
        "Chunks",
        1,
        len(chunks),
        min(10, len(chunks)),
    )

    for chunk in chunks[:chunks_to_show]:

        with st.expander(

            f"{chunk.file_path} | "
            f"Lines {chunk.start_line}-{chunk.end_line}"

        ):

            st.caption(
                f"Chunk #{chunk.chunk_index}"
            )

            st.code(
                chunk.content,
                language=(
                    chunk.language
                    if chunk.language != "unknown"
                    else None
                ),
            )

    st.markdown("</div>", unsafe_allow_html=True)

def render_future_query_section() -> None:

    st.markdown('<div class="main-card">', unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">5. Ask Questions About Repository</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.answer_generator is None:

        st.info("Please index a repository first.")

        st.markdown("</div>", unsafe_allow_html=True)
        return

    question = st.text_input(
        "Ask a question about the repository",
        placeholder="Where is HTML escaping implemented?",
    )

    if st.button("Get Answer"):

        if not question.strip():

            st.warning("Please enter a question.")

        else:

            try:

                with st.spinner("Searching repository and generating answer..."):

                    generator = st.session_state.answer_generator

                    result = generator.answer_question(
                    question=question,
                    top_k=5,
                    )

                    st.session_state.current_answer = result["answer"]

                    st.session_state.retrieved_sources = result["sources"]

            except Exception as error:

                st.error(str(error))

    if st.session_state.current_answer:

        st.divider()

        st.subheader("Answer")

        st.write(
            st.session_state.current_answer
        )

    if st.session_state.retrieved_sources:

        st.divider()

        st.subheader("Retrieved Sources")

        for chunk in st.session_state.retrieved_sources:

            with st.expander(

                f'{chunk["file_path"]} '
                f'({chunk["start_line"]}-{chunk["end_line"]})'

            ):

                st.write(
                    f'**Similarity Score:** '
                    f'{chunk["score"]:.4f}'
                )

                st.code(
                    chunk["content"],
                    language=chunk["language"]
                    if chunk["language"] != "unknown"
                    else None,
                )

    st.markdown("</div>", unsafe_allow_html=True)

def render_future_features_section() -> None:

    st.markdown('<div class="main-card">', unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">6. Project Status</div>',
        unsafe_allow_html=True,
    )

    indexed = st.session_state.answer_generator is not None

    st.checkbox(
        "Repository cloned",
        value=indexed,
        disabled=True,
    )

    st.checkbox(
        "Repository parsed",
        value=indexed,
        disabled=True,
    )

    st.checkbox(
        "Repository chunked",
        value=indexed,
        disabled=True,
    )

    st.checkbox(
        "Embeddings generated",
        value=indexed,
        disabled=True,
    )

    st.checkbox(
        "FAISS index built",
        value=indexed,
        disabled=True,
    )

    st.checkbox(
        "Metadata stored",
        value=indexed,
        disabled=True,
    )

    st.checkbox(
        "Semantic retrieval enabled",
        value=indexed,
        disabled=True,
    )

    st.checkbox(
        "Gemini answer generation enabled",
        value=indexed,
        disabled=True,
    )

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
