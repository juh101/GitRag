import streamlit as st

def render_header() -> None:
    st.markdown("""
        <div style="margin-bottom: 1.25rem;">
            <div class="hero-title">
                ✨ GitHub Repository AI Assistant
            </div>
            <div class="hero-subtitle">
                Understand any GitHub repository using Retrieval-Augmented Generation.
            </div>
            <div class="pipeline-ribbon">
                <span class="pipeline-step">Clone</span> →
                <span class="pipeline-step">Index</span> →
                <span class="pipeline-step">Retrieve</span> →
                <span class="pipeline-step">Ask Questions</span> →
                <span class="pipeline-step">Get Context-Aware Answers</span>
            </div>
        </div>
    """, unsafe_allow_html=True)