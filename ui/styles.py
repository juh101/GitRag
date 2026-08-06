import streamlit as st

def apply_theme(theme: str = "Dark") -> None:
    is_dark = theme == "Dark"

    # Precise palette contrast logic
    bg_app = "#080C14" if is_dark else "#F8FAFC"
    bg_surface = "#0D1322" if is_dark else "#FFFFFF"
    bg_card = "#111827" if is_dark else "#FFFFFF"
    bg_input = "#0B101D" if is_dark else "#F1F5F9"
    
    border_color = "#1E293B" if is_dark else "#CBD5E1"
    border_highlight = "#2563EB" if is_dark else "#0284C7"
    
    text_primary = "#F8FAFC" if is_dark else "#0F172A"
    text_secondary = "#94A3B8" if is_dark else "#334155"

    css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        /* Root App Container */
        html, body, [data-testid="stAppViewContainer"], .stApp {{
            background-color: {bg_app} !important;
            color: {text_primary} !important;
            font-family: 'Inter', sans-serif !important;
        }}

        /* Keep header container transparent so controls can render */
        header[data-testid="stHeader"] {{
            background-color: transparent !important;
            height: 3rem !important;
            z-index: 99999 !important;
        }}

        /* Force Pin the Sidebar Open/Close Toggle Button to Top Left */
        [data-testid="stSidebarCollapseButton"], 
        [data-testid="stSidebarExpandButton"],
        button[aria-label="Close sidebar"],
        button[aria-label="Open sidebar"],
        button[data-testid="baseButton-header"] {{
            visibility: visible !important;
            display: flex !important;
            position: fixed !important;
            top: 0.75rem !important;
            left: 0.75rem !important;
            z-index: 100000 !important;
            background-color: {bg_surface} !important;
            border: 1px solid {border_color} !important;
            border-radius: 8px !important;
            color: {text_primary} !important;
            padding: 0.25rem !important;
        }}

        /* Hide Default Chrome Footer */
        footer {{
            visibility: hidden !important;
            height: 0px !important;
        }}

        /* Native Sidebar Overrides */
        [data-testid="stSidebar"], [data-testid="stSidebarContent"] {{
            background-color: {bg_surface} !important;
            border-right: 1px solid {border_color} !important;
        }}

        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] span, 
        [data-testid="stSidebar"] label {{
            color: {text_primary} !important;
        }}

        /* Global Typography Rules */
        h1, h2, h3, h4, h5, h6, .card-header-title {{
            color: {text_primary} !important;
        }}

        p, span, label, .card-header-sub {{
            color: {text_secondary} !important;
        }}

        /* UI Cards */
        .glass-card {{
            background: {bg_card} !important;
            border: 1px solid {border_color} !important;
            border-radius: 14px;
            padding: 1.25rem;
            margin-bottom: 1rem;
        }}

        /* Input Controls and Buttons */
        .stTextInput>div>div>input {{
            background-color: {bg_input} !important;
            color: {text_primary} !important;
            border: 1px solid {border_color} !important;
            border-radius: 10px !important;
        }}

        .stButton>button {{
            border-radius: 8px !important;
            background-color: {bg_card} !important;
            color: {text_primary} !important;
            border: 1px solid {border_color} !important;
            font-weight: 600 !important;
        }}
        .stButton>button:hover {{
            border-color: {border_highlight} !important;
            color: {border_highlight} !important;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)