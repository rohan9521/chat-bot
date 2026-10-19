from langchain_core.messages import HumanMessage
import streamlit as st

import chatbot
def ui():
    st.set_page_config(page_title="Chatbot Workflow", page_icon=":robot_face:") 
    st.title("Chatbot Workflow")    

    user_input = st.chat_input("Enter your question")
    if 'message_history' not in st.session_state:
        st.session_state.message_history = []
            
    for message in st.session_state.message_history:
        with st.chat_message(message["role"]):
            st.text(message["content"])
            
    if user_input:
        st.session_state.message_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.text(user_input)
        try:
            response = chatbot.chatBot.invoke(
                {"messages": [HumanMessage(content=user_input)]},
                config=chatbot.config,
            )
            ai_message = response["messages"][-1]

            st.session_state.message_history.append(
                {"role": "assistant", "content": ai_message.content}
            )

            with st.chat_message("assistant"):
                st.text(ai_message.content)
        except Exception as e:
            st.error(f"Error: {e}")
   