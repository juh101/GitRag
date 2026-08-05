import streamlit as st


SUGGESTED_QUESTIONS = [
    "What is the overall architecture of this repository?",
    "Where is authentication implemented?",
    "Explain the project structure.",
    "Which files handle API requests?",
]


def render_chat() -> None:
    """
    Render the AI chat interface.
    """

    st.markdown("---")

    st.markdown(
        """
        <div class="section-title">
            💬 Ask Your Repository
        </div>
        <div class="section-subtitle">
            Ask anything about the indexed repository.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.repository_indexed:
        st.info("Index a repository to begin chatting.")
        return

    if not st.session_state.messages:

        st.markdown("#### Try asking")

        cols = st.columns(2)

        for i, question in enumerate(SUGGESTED_QUESTIONS):

            with cols[i % 2]:

                if st.button(
                    question,
                    key=f"suggestion_{i}",
                    use_container_width=True,
                ):

                    st.session_state.pending_question = question
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    prompt = None

    if "pending_question" in st.session_state:

        prompt = st.session_state.pending_question
        del st.session_state.pending_question

    else:

        prompt = st.chat_input(
            "Ask a question about this repository..."
        )

    if not prompt:
        return

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):

        st.markdown(prompt)

    with st.chat_message("assistant"):

        placeholder = st.empty()

        with st.spinner("Thinking..."):

            try:

                answer, sources = (
                    st.session_state.answer_generator.answer_question(
                        prompt
                    )
                )

                placeholder.markdown(answer)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

                st.session_state.current_answer = answer
                st.session_state.retrieved_sources = sources

            except Exception as error:

                placeholder.error(str(error))