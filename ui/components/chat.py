import time
import streamlit as st

def render_chat() -> None:
    st.markdown("""
        <div class="glass-card">
            <div class="card-header-title">🗨️ Ask Your Repository</div>
            <div class="card-header-sub">Ask questions to retrieve code and generate answers with Gemini.</div>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.get("repository_indexed"):
        st.info("Please index a GitHub repository above to start asking questions.")
        return

    # Suggested Prompt Buttons
    if not st.session_state.get("messages"):
        st.caption("Try asking:")
        p1, p2 = st.columns(2)
        p3, p4 = st.columns(2)

        if p1.button("↗ What is the overall architecture?", use_container_width=True):
            st.session_state.pending_question = "What is the overall architecture?"
        if p2.button("↗ Where is the core entry point?", use_container_width=True):
            st.session_state.pending_question = "Where is the core entry point?"
        if p3.button("↗ Explain the project structure.", use_container_width=True):
            st.session_state.pending_question = "Explain the project structure."
        if p4.button("↗ Which files handle main logic?", use_container_width=True):
            st.session_state.pending_question = "Which files handle main logic?"

    st.markdown("<br>", unsafe_allow_html=True)

    # Message History
    for msg in st.session_state.get("messages", []):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User Input
    user_query = st.chat_input("Ask a question about this repository...")
    if st.session_state.get("pending_question"):
        user_query = st.session_state.pop("pending_question")

    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            top_k = st.session_state.get("top_k", 5)
            
            with st.spinner("Retrieving sources & generating answer..."):
                try:
                    generator = st.session_state.answer_generator
                    result = generator.answer_question(question=user_query, top_k=top_k)

                    full_answer = result.get("answer", "")
                    srcs = result.get("sources", [])

                    # Response Streaming Effect
                    message_placeholder = st.empty()
                    chunked_text = ""
                    for char in full_answer.split(" "):
                        chunked_text += char + " "
                        message_placeholder.markdown(chunked_text + "▌")
                        time.sleep(0.02)
                    
                    message_placeholder.markdown(full_answer)

                    st.session_state.messages.append({"role": "assistant", "content": full_answer})
                    st.session_state.retrieved_sources = srcs
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")