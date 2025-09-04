import streamlit as st
from langgraph_backend import chatbot,retrieve_thread
from langchain_core.messages import HumanMessage,AIMessage,ToolMessage
import uuid

def generate_thread_id():
        thread_id=uuid.uuid4()
        return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
      return chatbot.get_state(config={'configurable': {'thread_id': thread_id}})

if 'message_history' not in st.session_state:
        st.session_state['message_history'] = []
    
if 'thread_id' not in st.session_state:
        st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
        st.session_state['chat_threads'] = retrieve_thread()

add_thread(st.session_state['thread_id'])

st.sidebar.title("Rohan's Langgraph Bot")
if st.sidebar.button("New chat"):
        reset_chat()
    
st.sidebar.header('My Conversations')
for thread_id in st.session_state['chat_threads']:
        if st.sidebar.button(str(thread_id)):
                st.session_state['thread_id']=thread_id
                state_snapshot = load_conversation(thread_id)
                if state_snapshot is None:
                        messages=[]
                else:
                        messages = state_snapshot.values['messages']

                temp_messages = []
                for msg in messages:
                        if isinstance(msg, HumanMessage):
                                role = "user"
                                content = msg.content
                        elif isinstance(msg, AIMessage):
                              role = "assistant"
                              content = msg.content
                        elif isinstance(msg, ToolMessage):
                              role = "tool"
                              content = msg.content
                        else:
                              role = "assistant"
                              content = str(msg)

                        temp_messages.append({"role": role, "content": content})

                st.session_state["message_history"] = temp_messages 
        
for message in st.session_state['message_history']:
      with st.chat_message(message["role"]):
        st.text(message['content'])

user_input = st.chat_input('Type here')

if user_input:
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)
    CONFIG = {
        "configurable": {"thread_id": st.session_state["thread_id"]},
        "metadata": {
            "thread_id": st.session_state["thread_id"]
        },
        "run_name": "chat_turn",
    }
    with st.chat_message('assistant'):
        status_holder = {"box": None}
        def ai_only_stream():
                for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages",
                ):
                      if isinstance(message_chunk,ToolMessage):

                        tool_name = getattr(message_chunk, "name", "tool")
                        if status_holder["box"] is None:
                                status_holder["box"] = st.status(
                                f"🔧 Using `{tool_name}` …", expanded=True
                        )
                        else:

                                status_holder["box"].update(
                                 label=f"🔧 Using `{tool_name}` …",
                                state="running",
                                expanded=True,
                        )
                      if isinstance(message_chunk, AIMessage):
                                yield message_chunk.content   
        ai_message = st.write_stream(ai_only_stream())
        if status_holder["box"] is not None:
            status_holder["box"].update(
                label="✅ Tool finished", state="complete", expanded=False
            )
     
                
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})



