import streamlit as st

def render_sources() -> None:
    st.markdown("""
        <div class="glass-card">
            <div class="card-header-title">📘 Sources</div>
            <div class="card-header-sub">Retrieved code snippets for the answer.</div>
        </div>
    """, unsafe_allow_html=True)

    sources = st.session_state.get("retrieved_sources", [])

    if not sources:
        st.info("No sources retrieved yet.")
        return

    for idx, src in enumerate(sources):
        f_path = src.get("file_path", f"file_{idx}.py")
        start_line = src.get("start_line", 1)
        end_line = src.get("end_line", 20)
        score = src.get("score", 0.90)
        content = src.get("content", "")
        lang = src.get("language", "python")

        match_pct = int(score * 100) if score <= 1.0 else int(score)

        st.markdown(f"""
            <div class="source-item-card">
                <div class="source-item-header">
                    <span class="source-item-file">📄 {f_path}</span>
                    <span class="source-item-match">{match_pct}% match</span>
                </div>
                <div class="source-item-lines">Lines {start_line} - {end_line} | Lang: <code>{lang}</code></div>
            </div>
        """, unsafe_allow_html=True)

        with st.expander(f"Inspect Snippet ({f_path})"):
            st.code(content, language=lang if lang != "unknown" else "python")