from langgraph.graph import StateGraph,START,END
from typing import TypedDict, Literal, Annotated
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
import operator

import os
import streamlit as st

os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
model = ChatGroq(model="llama-3.3-70b-versatile")

class Chatstate(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]

def chat_node(state:Chatstate):
    messages=state['messages']
    response=model.invoke(messages)
    return{'messages':[response]}

checkpointer=InMemorySaver()
graph=StateGraph(Chatstate)
graph.add_node('chat_node',chat_node)
graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)

chatbot=graph.compile(checkpointer=checkpointer)

