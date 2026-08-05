import streamlit as st


def render_sources() -> None:
    """
    Display the retrieved repository sources used to answer
    the latest question.
    """

    if not st.session_state.repository_indexed:
        return

    sources = st.session_state.retrieved_sources

    if not sources:
        return

    st.markdown("---")

    st.markdown(
        """
        <div class="section-title">
            📚 Sources
        </div>
        <div class="section-subtitle">
            These code snippets were retrieved from the repository
            before generating the answer.
        </div>
        """,
        unsafe_allow_html=True,
    )

    for index, source in enumerate(sources, start=1):

        similarity = source.get("score", 0.0)

        with st.container(border=True):

            col1, col2 = st.columns([5, 1])

            with col1:

                st.markdown(
                    f"### 📄 {source['file_name']}"
                )

                st.caption(source["file_path"])

                st.write(
                    f"**Lines:** "
                    f"{source['start_line']} - {source['end_line']}"
                )

            with col2:

                st.metric(
                    "Match",
                    f"{similarity * 100:.0f}%",
                )

            with st.expander("View Retrieved Code"):

                st.code(
                    source["content"],
                    language=(
                        source["language"]
                        if source["language"] != "unknown"
                        else None
                    ),
                )

        st.markdown("")