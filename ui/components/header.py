import streamlit as st


def render_header() -> None:
    """
    Render the application header.
    """

    st.markdown(
        """
        <div class="hero-card">

            <h1 style="margin-bottom:8px;">
                🤖 GitHub Repository AI Assistant
            </h1>

            <p style="font-size:18px; margin-bottom:4px;">
                Understand any GitHub repository using Retrieval-Augmented Generation.
            </p>

            <p style="opacity:0.75; margin-bottom:0;">
                Clone • Index • Retrieve • Ask Questions • Get Context-Aware Answers
            </p>

        </div>
        """,
        unsafe_allow_html=True,
    )