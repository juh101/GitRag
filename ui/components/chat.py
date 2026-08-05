import streamlit as st

def render_chat() -> None:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### 💬 Ask Your Repository")
    st.caption("Ask anything about the indexed repository.")

    if not st.session_state.get("repository_indexed"):
        st.info("Please index a GitHub repository above to unlock the Copilot workspace.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # Suggested Prompts Section
    if not st.session_state.get("messages"):
        st.write("Try asking:")
        q1, q2 = st.columns(2)
        q3, q4 = st.columns(2)

        if q1.button("↗ What is the overall architecture?", use_container_width=True):
            st.session_state.pending_question = "What is the overall architecture?"
        if q2.button("↗ Where is authentication implemented?", use_container_width=True):
            st.session_state.pending_question = "Where is authentication implemented?"
        if q3.button("↗ Explain the project structure.", use_container_width=True):
            st.session_state.pending_question = "Explain the project structure."
        if q4.button("↗ Which files handle API requests?", use_container_width=True):
            st.session_state.pending_question = "Which files handle API requests?"

    # Message History Rendering
    for msg in st.session_state.get("messages", []):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Handle Input OR Suggested Click
    query_input = st.chat_input("Ask a question about this repository...")
    if st.session_state.get("pending_question"):
        query_input = st.session_state.pop("pending_question")

    if query_input:
        st.session_state.messages.append({"role": "user", "content": query_input})
        with st.chat_message("user"):
            st.markdown(query_input)

        with st.chat_message("assistant"):
            with st.spinner("Retrieving relevant code and analyzing context..."):
                try:
                    generator = st.session_state.answer_generator
                    result = generator.answer_question(question=query_input, top_k=5)

                    answer = result.get("answer", "")
                    sources = result.get("sources", [])

                    st.markdown(answer)
                    
                    st.session_state.current_answer = answer
                    st.session_state.retrieved_sources = sources
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating answer: {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)