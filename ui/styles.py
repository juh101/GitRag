import streamlit as st


def apply_theme(theme: str) -> None:
    """Apply the application theme."""

    if theme == "Dark":
        bg = "#0F172A"
        surface = "#1E293B"
        border = "#334155"
        text = "#F8FAFC"
        muted = "#94A3B8"
        primary = "#3B82F6"
        hover = "#2563EB"
    else:
        bg = "#F8FAFC"
        surface = "#FFFFFF"
        border = "#E2E8F0"
        text = "#111827"
        muted = "#6B7280"
        primary = "#2563EB"
        hover = "#1D4ED8"

    st.markdown(
        f"""
<style>

footer {{
    visibility: hidden;
}}

.block-container {{
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}}

.stApp {{
    background: {bg};
}}

section[data-testid="stSidebar"] {{
    border-right: 1px solid {border};
}}

.hero-card,
.repository-card,
.answer-card,
.source-card {{
    background: {surface};
    border: 1px solid {border};
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 20px;
}}

.answer-card {{
    border-left: 5px solid {primary};
}}

.section-title {{
    font-size: 1.6rem;
    font-weight: 700;
    color: {text};
    margin-bottom: .25rem;
}}

.section-subtitle {{
    color: {muted};
    margin-bottom: 1.2rem;
}}

div[data-testid="stTextInput"] input {{
    border-radius: 12px;
    border: 1px solid {border};
}}

div[data-testid="stTextArea"] textarea {{
    border-radius: 12px;
    border: 1px solid {border};
}}

div[data-testid="stButton"] > button {{
    width: 100%;
    border-radius: 12px;
    border: none;
    background: {primary};
    color: white;
    font-weight: 600;
    padding: .7rem;
}}

div[data-testid="stButton"] > button:hover {{
    background: {hover};
}}

div[data-testid="stMetric"] {{
    background: {surface};
    border: 1px solid {border};
    border-radius: 16px;
    padding: 12px;
}}

div[data-testid="stExpander"] {{
    border: 1px solid {border};
    border-radius: 14px;
}}

pre {{
    border-radius: 12px !important;
}}

::-webkit-scrollbar {{
    width: 8px;
}}

::-webkit-scrollbar-thumb {{
    background: {border};
    border-radius: 8px;
}}

</style>
""",
        unsafe_allow_html=True,
    )