import streamlit as st

def render_sources() -> None:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### 📘 Sources")
    st.caption("Retrieved code snippets for the answer.")

    sources = st.session_state.get("retrieved_sources", [])

    if not sources:
        st.info("No sources retrieved yet. Ask a question to view matching code context.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    for idx, src in enumerate(sources):
        file_path = src.get("file_path", f"File {idx+1}")
        start_line = src.get("start_line", 0)
        end_line = src.get("end_line", 0)
        score = src.get("score", 0.0)
        content = src.get("content", "")
        lang = src.get("language", "python")

        match_pct = int(score * 100) if score <= 1.0 else min(int(score), 99)

        st.markdown(f"""
            <div class="source-card">
                <div class="source-card-header">
                    <span class="source-filename">📄 {file_path}</span>
                    <span class="status-badge-green">{match_pct}% match</span>
                </div>
                <div class="source-lines">Lines {start_line} - {end_line}</div>
            </div>
        """, unsafe_allow_html=True)

        with st.expander(f"Inspect Snippet ({file_path})"):
            st.code(
                content,
                language=lang if lang != "unknown" else None
            )

    st.markdown('</div>', unsafe_allow_html=True)