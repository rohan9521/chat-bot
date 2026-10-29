from typing import Literal, TypedDict
from uuid import uuid4


class ChatMessage(TypedDict):
    role: Literal["user", "assistant"]
    content: str


class ChatSession(TypedDict):
    title: str
    messages: list[ChatMessage]


def create_thread() -> tuple[str, ChatSession]:
    thread_id = uuid4().hex
    return thread_id, {"title": "New chat", "messages": []}


def get_active_thread(
    chat_sessions: dict[str, ChatSession],
    active_chat_id: str | None,
) -> tuple[str, ChatSession]:
    if active_chat_id is not None and active_chat_id in chat_sessions:
        return active_chat_id, chat_sessions[active_chat_id]

    if not chat_sessions:
        raise ValueError("Cannot select an active chat when no chats exist.")

    return next(iter(chat_sessions.items()))
 