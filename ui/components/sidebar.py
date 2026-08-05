import streamlit as st


def render_sidebar() -> str:
    """
    Render the application sidebar.
    """

    with st.sidebar:

        st.title("⚙️ Settings")

        theme = st.radio(
            "Theme",
            ["Light", "Dark"],
            horizontal=True,
        )

        st.divider()

        st.subheader("Repository")

        if st.session_state.repository_indexed:

            st.success("Repository Indexed")

            st.write(
                f"**{st.session_state.repository_owner}"
                f"/{st.session_state.repository_name}**"
            )

        else:

            st.info("No repository loaded.")

        st.divider()

        st.subheader("Quick Actions")

        if st.button(
            "🗑️ Clear Conversation",
            use_container_width=True,
        ):

            st.session_state.messages = []
            st.session_state.current_answer = ""
            st.session_state.retrieved_sources = []

            st.rerun()

        st.divider()

        st.subheader("About")

        st.caption(
            "GitHub Repository AI Assistant uses semantic search "
            "with FAISS and Gemini to answer repository-specific questions."
        )

        st.caption("Made with ❤️ using Streamlit")

    return theme