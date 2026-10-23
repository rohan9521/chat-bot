from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from typing import Annotated, List, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages   
from langgraph.checkpoint.memory import InMemorySaver

ollamaLLM = ChatOllama(
    model="llama3",
    base_url="http://localhost:11434",  
    temperature=0.7,
    streaming=True,
)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant use the following guidelines to answer the question use the language and tone specified in the input.use language{language} and tone{tone} and role{role}"),
        ("user", "{user_question}"),
    ]
)


class ChatState(TypedDict ):
    messages: Annotated[List[BaseMessage], add_messages]
    

graph = StateGraph(ChatState)

def chat_node(state:ChatState):
    messages = state["messages"]
    response = ollamaLLM.invoke(messages)
    return {"messages": [response]}

graph.add_node('chat_node',chat_node)

graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)

checkpointer = InMemorySaver()
chatBot = graph.compile(checkpointer=checkpointer)
threadId = "thread2"

config = {"configurable": {"thread_id": "chat-1"}}  

chatBot


