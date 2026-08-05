import streamlit as st

def render_sidebar() -> None:
    st.sidebar.markdown("### 🐙 GitHub Repository\n**AI Assistant**")
    st.sidebar.caption("Understand any repository using Retrieval-Augmented Generation")

    st.sidebar.markdown("---")
    st.sidebar.write("**Theme**")
    
    # Light/Dark Toggle logic
    selected_theme = st.sidebar.radio(
        "Theme Toggle",
        options=["Dark", "Light"],
        index=0 if st.session_state.get("theme", "Dark") == "Dark" else 1,
        label_visibility="collapsed",
        horizontal=True
    )
    if selected_theme != st.session_state.get("theme"):
        st.session_state.theme = selected_theme
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.write("**Repository**")

    if st.session_state.get("repository_indexed"):
        owner = st.session_state.get("repository_owner", "owner")
        repo = st.session_state.get("repository_name", "repo")
        st.sidebar.markdown(f"""
            <div style="background: #0F172A; border: 1px solid #1E293B; padding: 0.75rem; border-radius: 8px;">
                <span class="status-badge-green">● Repository Indexed</span>
                <div style="margin-top: 0.4rem; font-weight: 600; font-size: 0.85rem;">{owner}/{repo}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.info("No repository indexed yet.")

    st.sidebar.markdown("---")
    st.sidebar.write("**Quick Actions**")
    if st.sidebar.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_answer = ""
        st.session_state.retrieved_sources = []
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.write("**About**")
    st.sidebar.caption(
        "GitHub Repository AI Assistant uses semantic search with FAISS "
        "and Gemini to answer repository-specific questions."
    )
    st.sidebar.caption("Made with 💜 using Streamlit")