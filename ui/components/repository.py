import streamlit as st

from llm.answer_generator import AnswerGenerator
from llm.llm_client import LLMClient
from llm.prompt_builder import PromptBuilder
from retrieval.vector_retriever import VectorRetriever
from scripts.index_repository import ingest_repository


def render_repository() -> None:
    """
    Repository indexing section.
    """

    st.markdown(
        """
        <div class="hero-card">
            <div class="section-title">
                📂 Repository
            </div>
            <div class="section-subtitle">
                Index a GitHub repository and make it searchable using semantic retrieval.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    repo_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/pallets/flask",
    )

    col1, col2 = st.columns([5, 1])

    with col2:
        index_clicked = st.button(
            "Index",
            use_container_width=True,
        )

    if not index_clicked:
        return

    if not repo_url.strip():
        st.warning("Please enter a GitHub repository URL.")
        return

    try:

        progress = st.progress(0)

        with st.spinner("Cloning repository..."):
            progress.progress(15)

            (
                repository_path,
                documents,
                chunks,
            ) = ingest_repository(repo_url)

        progress.progress(55)

        with st.spinner("Loading retrieval pipeline..."):

            retriever = VectorRetriever(repository_path)

            answer_generator = AnswerGenerator(
                retriever=retriever,
                llm_client=LLMClient(),
                prompt_builder=PromptBuilder(),
            )

        progress.progress(100)

        st.session_state.repository_path = repository_path

        st.session_state.repository_owner = (
            repository_path.parent.name
        )

        st.session_state.repository_name = (
            repository_path.name
        )

        st.session_state.documents = documents
        st.session_state.chunks = chunks

        st.session_state.answer_generator = answer_generator
        st.session_state.retriever = retriever

        st.session_state.repository_indexed = True

        st.session_state.current_answer = ""
        st.session_state.retrieved_sources = []

        st.session_state.stats = {
            "files": len(documents),
            "chunks": len(chunks),
            "languages": len(
                {
                    doc.language
                    for doc in documents
                }
            ),
        }

        progress.empty()

        st.success("Repository indexed successfully.")

        st.markdown("### Repository Details")

        c1, c2 = st.columns(2)

        with c1:

            st.write("**Owner**")
            st.write(st.session_state.repository_owner)

        with c2:

            st.write("**Repository**")
            st.write(st.session_state.repository_name)

    except Exception as error:

        st.error(str(error))