import streamlit as st


def render_answer() -> None:
    """
    Render repository overview.
    """

    if not st.session_state.repository_indexed:
        return

    st.markdown("---")

    st.markdown(
        """
        <div class="section-title">
            📋 Repository Overview
        </div>
        <div class="section-subtitle">
            Current workspace information.
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([2, 1])

    with left:

        st.markdown(
            f"""
<div class="repository-card">

### 📂 {st.session_state.repository_name}

**Owner**

{st.session_state.repository_owner}

**Status**

🟢 Indexed and ready for questions

</div>
""",
            unsafe_allow_html=True,
        )

    with right:

        stats = st.session_state.stats

        st.metric(
            "Files",
            stats["files"],
        )

        st.metric(
            "Chunks",
            stats["chunks"],
        )

        st.metric(
            "Languages",
            stats["languages"],
        )