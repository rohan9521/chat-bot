from collections.abc import Iterator
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
import sqlite3

from threads import ChatMessage, ChatSession


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


llm = ChatOllama(
    model="llama3",
    base_url="http://localhost:11434",
    temperature=0.7,
    streaming=True,
)


def chat_node(state: ChatState) -> dict[str, list[BaseMessage]]:
    return {"messages": [llm.invoke(state["messages"])]}


graph = StateGraph(ChatState)
graph.add_node("chat", chat_node)
graph.add_edge(START, "chat")
graph.add_edge("chat", END)

connection = sqlite3.connect("chat_graph.db",check_same_thread=False)

checkpointer = SqliteSaver(connection)

chat_graph = graph.compile(checkpointer=checkpointer)

def chat_session_from_messages(messages: list[BaseMessage]) -> ChatSession:
    chat_messages: list[ChatMessage] = []
    for message in messages:
        if message.type == "human":
            role = "user"
        elif message.type == "ai":
            role = "assistant"
        else:
            raise ValueError(f"Unsupported chat message type: {message.type}")

        if not isinstance(message.content, str):
            raise TypeError("Chat messages must contain text.")

        chat_messages.append({"role": role, "content": message.content})

    first_user_message = next(
        (message["content"] for message in chat_messages if message["role"] == "user"),
        "",
    )
    title = " ".join(first_user_message.split())
    if not title:
        title = "New chat"
    elif len(title) > 32:
        title = f"{title[:29]}..."

    return {"title": title, "messages": chat_messages}


def get_all_threads() -> dict[str, ChatSession]:
    all_threads: dict[str, ChatSession] = {}
    for checkpoint in checkpointer.list(None):
        thread_id = checkpoint.config["configurable"]["thread_id"]

        if thread_id in all_threads:
            continue

        messages = checkpoint.checkpoint['channel_values'].get("messages")
        if messages is not None:
            all_threads[thread_id] = chat_session_from_messages(messages)
    return all_threads

def stream_response(question: str, thread_id: str) -> Iterator[str]:
    for chunk, _metadata in chat_graph.stream(
        {"messages": [HumanMessage(content=question)]},
        config={"configurable": {"thread_id": thread_id}},
        stream_mode="messages",
    ):
        content = getattr(chunk, "content", "")
        if isinstance(content, str) and content:
            yield content
