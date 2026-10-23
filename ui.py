from uuid import uuid4

from langchain_core.messages import HumanMessage
import streamlit as st

import chatbot


def ui():
    st.set_page_config(page_title="Chatbot Workflow", page_icon=":robot_face:")
    st.title("Chatbot Workflow")

    if "chat_sessions" not in st.session_state:
        initial_chat_id = uuid4().hex
        st.session_state.chat_sessions = {
            initial_chat_id: {"title": "New chat", "messages": []}
        }
        st.session_state.active_chat_id = initial_chat_id

    with st.sidebar:
        st.title("Chat sessions")
        if st.button("＋ New chat", use_container_width=True):
            new_chat_id = uuid4().hex
            st.session_state.chat_sessions[new_chat_id] = {
                "title": "New chat",
                "messages": [],
            }
            st.session_state.active_chat_id = new_chat_id

        for chat_id, session in st.session_state.chat_sessions.items():
            if st.button(
                session["title"],
                key=f"chat-{chat_id}",
                type="primary"
                if chat_id == st.session_state.active_chat_id
                else "secondary",
                use_container_width=True,
            ):
                st.session_state.active_chat_id = chat_id

    active_chat_id = st.session_state.active_chat_id
    active_session = st.session_state.chat_sessions[active_chat_id]

    for message in active_session["messages"]:
        with st.chat_message(message["role"]):
            st.text(message["content"])

    user_input = st.chat_input("Enter your question")
    if user_input:
        active_session["messages"].append(
            {"role": "user", "content": user_input}
        )
        if active_session["title"] == "New chat":
            title = " ".join(user_input.split())
            active_session["title"] = (
                title if len(title) <= 32 else f"{title[:29]}..."
            )

        with st.chat_message("user"):
            st.text(user_input)

        try:
            def response_chunks():
                for chunk, _metadata in chatbot.chatBot.stream(
                    {"messages": [HumanMessage(content=user_input)]},
                    config={"configurable": {"thread_id": active_chat_id}},
                    stream_mode="messages",
                ):
                    text = getattr(chunk, "content", chunk)
                    if isinstance(text, str) and text:
                        yield text

            with st.chat_message("assistant"):
                ai_message = st.write_stream(response_chunks())

            active_session["messages"].append(
                {"role": "assistant", "content": ai_message}
            )

        except Exception as e:
            st.error(f"Error: {e}")
        else:
            st.rerun()
   