import streamlit as st

def apply_theme(theme: str = "Dark") -> None:
    is_dark = theme == "Dark"

    # Precise palette targeting the mock-up UI
    bg_app = "#0B0F19" if is_dark else "#F4F6F9"
    bg_surface = "#111827" if is_dark else "#FFFFFF"
    bg_card = "#161F33" if is_dark else "#FFFFFF"
    bg_input = "#0F172A" if is_dark else "#EDF2F7"
    border_color = "#1E293B" if is_dark else "#E2E8F0"
    border_active = "#3B82F6" if is_dark else "#2563EB"
    
    text_primary = "#F8FAFC" if is_dark else "#0F172A"
    text_secondary = "#94A3B8" if is_dark else "#475569"
    
    badge_green_bg = "rgba(16, 185, 129, 0.15)" if is_dark else "rgba(16, 185, 129, 0.1)"
    badge_green_txt = "#10B981"

    css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        /* Root App Container */
        html, body, [data-testid="stAppViewContainer"] {{
            background-color: {bg_app} !important;
            color: {text_primary} !important;
            font-family: 'Inter', sans-serif !important;
        }}

        /* Hide Streamlit Header & Footer Chrome */
        header[data-testid="stHeader"], footer {{
            visibility: hidden !important;
            height: 0px !important;
        }}

        .main .block-container {{
            padding-top: 1rem !important;
            padding-bottom: 1.5rem !important;
            max-width: 98% !important;
        }}

        /* Sidebar Styling */
        [data-testid="stSidebar"] {{
            background-color: {bg_surface} !important;
            border-right: 1px solid {border_color} !important;
        }}

        /* Typography Override */
        h1, h2, h3, h4, h5, h6 {{
            color: {text_primary} !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: -0.01em !important;
        }}

        /* Universal Glass Card Styling */
        .glass-card {{
            background-color: {bg_card};
            border: 1px solid {border_color};
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        }}

        /* Header Hero Container */
        .hero-title {{
            text-align: center;
            font-size: 1.75rem;
            font-weight: 800;
            background: linear-gradient(135deg, #FACC15 0%, #F59E0B 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }}
        
        .hero-subtitle {{
            text-align: center;
            color: {text_secondary};
            font-size: 0.9rem;
            margin-top: 0.25rem;
            margin-bottom: 0.75rem;
        }}

        /* Pipeline Flow Badge Ribbon */
        .pipeline-ribbon {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 0.5rem;
            flex-wrap: wrap;
            font-size: 0.8rem;
            color: {text_secondary};
        }}
        .pipeline-step {{
            background: {bg_input};
            border: 1px solid {border_color};
            padding: 0.25rem 0.6rem;
            border-radius: 6px;
            color: {text_primary};
        }}

        /* Repository Metrics Header Cards */
        .metric-box {{
            background: {bg_input};
            border: 1px solid {border_color};
            border-radius: 10px;
            padding: 0.75rem 1rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}
        .metric-icon {{
            font-size: 1.25rem;
            color: {border_active};
        }}
        .metric-val {{
            font-weight: 700;
            font-size: 1.1rem;
            color: {text_primary};
            line-height: 1;
        }}
        .metric-lbl {{
            font-size: 0.75rem;
            color: {text_secondary};
        }}

        /* Custom Status Badges */
        .status-badge-green {{
            background-color: {badge_green_bg};
            color: {badge_green_txt};
            font-weight: 600;
            font-size: 0.75rem;
            padding: 0.2rem 0.5rem;
            border-radius: 6px;
            display: inline-block;
        }}

        /* Perplexity Code Source Cards */
        .source-card {{
            background: {bg_card};
            border: 1px solid {border_color};
            border-radius: 10px;
            padding: 0.85rem;
            margin-bottom: 0.75rem;
        }}
        .source-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.35rem;
        }}
        .source-filename {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            font-weight: 600;
            color: {border_active};
        }}
        .source-lines {{
            font-size: 0.75rem;
            color: {text_secondary};
        }}

        /* Code Block Override */
        code, pre {{
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.8rem !important;
            background-color: {bg_input} !important;
        }}

        /* Button Styling Overrides */
        .stButton>button {{
            border-radius: 8px !important;
            background-color: {bg_card} !important;
            color: {text_primary} !important;
            border: 1px solid {border_color} !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }}
        .stButton>button:hover {{
            border-color: {border_active} !important;
            color: {border_active} !important;
            background-color: {bg_input} !important;
        }}

        /* Input Controls Override */
        .stTextInput>div>div>input {{
            background-color: {bg_input} !important;
            color: {text_primary} !important;
            border: 1px solid {border_color} !important;
            border-radius: 8px !important;
        }}
        .stTextInput>div>div>input:focus {{
            border-color: {border_active} !important;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)