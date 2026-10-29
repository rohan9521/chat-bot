import streamlit as st

import chatbot
from threads import ChatSession, create_thread, get_active_thread

def _create_chat(chat_sessions: dict[str, ChatSession]) -> None:
    thread_id, session = create_thread()
    chat_sessions[thread_id] = session
    st.session_state.active_chat_id = thread_id


def _select_chat(chat_id: str) -> None:
    st.session_state.active_chat_id = chat_id


def _initialize_chat_sessions() -> dict[str, ChatSession]:
    chat_sessions: dict[str, ChatSession] = st.session_state.setdefault(
        "chat_sessions", {},
    )
    chat_sessions.update(chatbot.get_all_threads())
    for thread_id, session in list(chat_sessions.items()):
        if isinstance(session, list):
            chat_sessions[thread_id] = chatbot.chat_session_from_messages(session)

    st.session_state.setdefault("active_chat_id", None)
    if not chat_sessions:
        _create_chat(chat_sessions)
    return chat_sessions


def _render_sidebar(chat_sessions: dict[str, ChatSession]) -> None:
    with st.sidebar:
        st.title("Chat sessions")
        if st.button(
            "New chat",
            icon=":material/add:",
            width="stretch",
        ):
            _create_chat(chat_sessions)
    
        for chat_id, session in chat_sessions.items():
            st.button(
                session["title"],
                key=f"chat-{chat_id}",
                type=(
                    "primary"
                    if chat_id == st.session_state.active_chat_id
                    else "secondary"
                ),
                width="stretch",
                on_click=_select_chat,
                args=(chat_id,),
            )


def _render_chat_history(session: ChatSession) -> None:
    for message in session["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def _handle_user_input(user_input: str, session: ChatSession) -> None:
    session["messages"].append({"role": "user", "content": user_input})
    if session["title"] == "New chat":
        title = " ".join(user_input.split())
        session["title"] = title if len(title) <= 32 else f"{title[:29]}..."

    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        with st.chat_message("assistant"):
            assistant_message = st.write_stream(
                chatbot.stream_response(user_input, st.session_state.active_chat_id)
            )

        session["messages"].append(
            {"role": "assistant", "content": assistant_message}
        )
    except Exception as error:
        st.error(f"Unable to generate a response: {error}")
    else:
        st.rerun()


def render_app() -> None:
    st.set_page_config(page_title="Chat Assistant", page_icon=":robot_face:")
    
    st.title("Chat Assistant")

    chat_sessions = _initialize_chat_sessions()
    active_chat_id, active_session = get_active_thread(
        chat_sessions,
        st.session_state.active_chat_id,
    )
    st.session_state.active_chat_id = active_chat_id

    _render_sidebar(chat_sessions)
    _render_chat_history(active_session)

    if user_input := st.chat_input("Enter your question"):
        _handle_user_input(user_input, active_session)
