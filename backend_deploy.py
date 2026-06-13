from langgraph.graph import StateGraph,START,END
from typing import TypedDict, Literal, Annotated
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
# from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from supabase import create_client, Client
from dotenv import load_dotenv

import os
import streamlit as st
load_dotenv()

supabase: Client=create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# groq_api_key = os.getenv("GROQ_API_KEY")
# os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
# model = ChatGroq(model="meta-llama/llama-prompt-guard-2-22m")
model = ChatOpenAI(
    model="nvidia/nemotron-3-nano-30b-a3b:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

class Chatstate(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]

search_tool=DuckDuckGoSearchRun(region="us-en")
model_with_tool=model.bind_tools([search_tool])

def chat_node(state:Chatstate):
    messages=state['messages']
    response=model_with_tool.invoke(messages)
    return{'messages':[response]}


tool_node=ToolNode([search_tool])

checkpointer=InMemorySaver()
graph=StateGraph(Chatstate)

graph.add_node('chat_node',chat_node)
graph.add_node('tools',tool_node)
graph.add_edge(START,'chat_node')
graph.add_conditional_edges("chat_node",tools_condition)
graph.add_edge("tools", "chat_node")

chatbot=graph.compile(checkpointer=checkpointer)


def save_message(thread_id:str, role:str, content:str):
    """Save a single message to Supabase."""
    if not content:
        return
    supabase.table("chat_messages").insert({
        "thread_id":thread_id,
        "role":role,
        "content":content
    }).execute()

def load_thread_messages(thread_id:str)->list[dict]:
    """ Load all messages for a thread from Supabase."""
    result=supabase.table("chat_messages") \
        .select("role,content") \
        .eq("thread_id",thread_id) \
        .order("created_at") \
        .execute()
    return result.data

def get_all_threads() -> list[str]:
    """Get all unique thread IDs from Supabase."""
    result = supabase.table("chat_messages") \
        .select("thread_id") \
        .order("created_at", desc=True) \
        .execute()
    seen=[]
    for row in result.data:
        if row["thread_id"] not in seen:
            seen.append(row["thread_id"])

    return seen