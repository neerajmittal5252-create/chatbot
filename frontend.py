import streamlit as st
from backend_deploy import chatbot
from langchain_core.messages import HumanMessage
import uuid

def generate_thread_id():
    thread_id=str(uuid.uuid4())
    return thread_id


def reset_chat():
    thread_id=generate_thread_id()
    st.session_state['thread_id']=thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history']=[]

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    return chatbot.get_state(config={'configurable':{'thread_id':str(thread_id)}}).values['messages']

st.title("Sigma Chat AI")

if 'message_history' not in st.session_state:
    st.session_state['message_history']=[]

if 'thread_id' not in st.session_state:
    st.session_state['thread_id']=generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads']=[]

add_thread(st.session_state['thread_id'])

st.sidebar.title("Sigma AI")

if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("My Conversations")

for thread_id in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id']=thread_id
        messages=load_conversation(thread_id)
        temp_messages=[]
        for message in messages:
            if isinstance(message,HumanMessage):
                role='user'
            else:
                role='assistant'
            temp_messages.append({'role':role,'content':message.content})
        st.session_state['message_history']=temp_messages

for message in st.session_state['message_history']:
    if message["content"]:
        with st.chat_message(message['role']):
            st.text(message['content'])

user_message=st.chat_input('Type Here: ')
if user_message:
    st.session_state['message_history'].append({'role':'user','content':user_message})
    with st.chat_message('user'):
        st.text(user_message)

    config={'configurable':{'thread_id':str(st.session_state['thread_id'])}}

    # response=chatbot.invoke({'messages':[HumanMessage(content=user_message)]},config=config)
    # ai_message=response['messages'][-1].content
    # st.session_state['message_history'].append({'role':'assistant','content':ai_message})
    with st.chat_message('assistant'):
        response=st.write_stream(
                    message_chunk.content
                    for message_chunk, metadata in chatbot.stream(
                        {"messages": [HumanMessage(content=user_message)]},
                        config=config,
                        stream_mode="messages",
                    )
                    if getattr(message_chunk, "content", None)
        )
    st.session_state["message_history"].append(
    {"role": "assistant", "content": response}
    )



