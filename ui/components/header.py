import streamlit as st

def render_header() -> None:
    st.markdown("""
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <div style="font-size: 1.85rem; font-weight: 800; display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
                ✨ GitHub Repository AI Assistant
            </div>
            <div style="font-size: 0.95rem; margin-top: 0.35rem;">
                Understand any GitHub repository using Retrieval-Augmented Generation.
            </div>
        </div>
    """, unsafe_allow_html=True)