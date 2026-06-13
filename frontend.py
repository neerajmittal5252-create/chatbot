import streamlit as st
from backend_deploy import chatbot, save_message, load_thread_messages, get_all_threads
from langchain_core.messages import HumanMessage,AIMessage, ToolMessage, AIMessageChunk
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
    # return chatbot.get_state(
    #     config={'configurable':{
    #         'thread_id': str(thread_id)
    #     }}
    # ).values.get('messages', [])
    return load_thread_messages(thread_id)

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

all_threads=get_all_threads()

for thread_id in all_threads:
    label=thread_id[:8]+"..."
    if st.sidebar.button(label,key=thread_id):
        st.session_state['thread_id']=thread_id
        st.session_state['message_history'] = load_conversation(thread_id)

for message in st.session_state['message_history']:
    if message["content"]:
        with st.chat_message(message['role']):
            st.text(message['content'])

# for thread_id in st.session_state['chat_threads'][::-1]:
#     if st.sidebar.button(str(thread_id)):
#         st.session_state['thread_id']=thread_id
#         messages=load_conversation(thread_id)
#         temp_messages=[]
#         for message in messages:
#             if isinstance(message,HumanMessage):
#                 role='user'
#             elif isinstance(message, AIMessage):
#                 role = "assistant"
#             elif isinstance(message, ToolMessage):
#                 continue 
#             temp_messages.append({'role':role,'content':message.content})
#         st.session_state['message_history']=temp_messages

# for message in st.session_state['message_history']:
#     if message["content"]:
#         with st.chat_message(message['role']):
#             st.text(message['content'])

user_message=st.chat_input('Type Here: ')
if user_message:
    st.session_state['message_history'].append({'role':'user','content':user_message})
    with st.chat_message('user'):
        st.text(user_message)

    save_message(st.session_state['thread_id'],'user',user_message)
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
                    if isinstance(message_chunk, AIMessageChunk)
                    and message_chunk.content
        )
    save_message(st.session_state['thread_id'], 'assistant', response)
    st.session_state["message_history"].append(
    {"role": "assistant", "content": response}
    )



