import streamlit as st


def render_stats() -> None:
    """
    Render repository statistics.
    """

    if not st.session_state.repository_indexed:
        return

    stats = st.session_state.stats

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="section-title">
            📊 Repository Overview
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Files",
            value=stats["files"],
        )

    with col2:
        st.metric(
            label="Code Chunks",
            value=stats["chunks"],
        )

    with col3:
        st.metric(
            label="Languages",
            value=stats["languages"],
        )

    st.markdown("---")