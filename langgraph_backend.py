from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated
from langchain_core.messages import BaseMessage,HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
import requests
import os


load_dotenv()
llm=ChatOpenAI()

search_tool=DuckDuckGoSearchRun(region='us-en')

 
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    if operation == "add":
        result = first_num + second_num
    elif operation == "sub":
        result = first_num - second_num
    elif operation == "mul":
        result = first_num * second_num
    elif operation == "div":
        if second_num == 0:
            return {"error": "Division by zero is not allowed"}
        result = first_num / second_num
    else:
        return {"error": f"Unsupported operation '{operation}'"}
        
    return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}

def get_stock_price(symbol:str)->dict:
     """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
     api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
     url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
     r=requests.get(url)
     return r.json()

tools=[search_tool,get_stock_price,calculator]
llm_with_tools=llm.bind_tools(tools=tools)


class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages]

def chat_node(state:ChatState):
    messages= state['messages']
    response=llm_with_tools.invoke(messages)
    return {"messages":[response]}

tool_node=ToolNode(tools)

conn=sqlite3.connect(database='chatbot.db',check_same_thread=False)
checkpointer=SqliteSaver(conn=conn)

graph = StateGraph(ChatState)
graph.add_node("chat_node",chat_node)
graph.add_node("tools",tool_node)
graph.add_edge(START,'chat_node')
graph.add_conditional_edges("chat_node",tools_condition)
graph.add_edge('tools','chat_node')
chatbot=graph.compile(checkpointer=checkpointer)

def retrieve_thread():
    thread_set=set()
    for checkpoint in checkpointer.list(None):
        thread_set.add(checkpoint.config['configurable']['thread_id'])
    return list(thread_set)

print("done!")