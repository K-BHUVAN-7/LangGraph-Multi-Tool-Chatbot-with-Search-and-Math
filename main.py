#IMPORT THE NECESSARY LIBRARIES
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from langchain_tavily import TavilySearch
import dotenv
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition

# Load environment variables from .env file
load_dotenv()
os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY"

# Define state
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Create LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key=os.environ["GOOGLE_API_KEY"])

# Node function
def chatbot(state: State) -> State:
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# Build graph
graph = StateGraph(State)
graph.add_node("chatbot", chatbot)
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)

# Compile graph
app = graph.compile()

# Run
#result = app.invoke({"messages": ["Hello!"]})
#print(result)
for i in app.stream({"messages":["hi? how are you?"]}):
    for value in i.values():
        print(value["messages"][-1].content)  # Print the last message in the stream
# Define tools
tool=TavilySearch(max_results=5)
final=tool.invoke("who is ronaldo?")
print(final)

#DEFINING THE CUSTOM TOOL
def multiple(a: int, b: int) -> int:
    """
    take two integers and return their product
    a is the first integer
    b is the second integer
    returns the product of a and b
    """
    return a * b
#CREATING THE LIST FOR THE TOOLS

tools=[tool,multiple]
def tool_calling_llm(state: State) -> State:
    response = llm.invoke(state["messages"], tools=tools)
    return {"messages": [response]}

#CREATING THE GRAPH
tool_graph=StateGraph(State)

#DEFINING THE NODES

tool_graph.add_node("tool_calling_llm", tool_calling_llm)
tool_graph.add_node("llm_tools",ToolNode(tools))

#DEFINING THE EDGES 
tool_graph.add_edge(START,"tool_calling_llm")
tool_graph.add_conditional_edges(
    "tool_calling_llm",
    tools_condition,
    {
        "tools": "llm_tools",
        END: END
    }
)
tool_graph.add_edge("llm_tools",END)
final_result=tool_graph.compile()
ouput=final_result.invoke({"messages":["what is the product of 2 and 3?"]})
ouput["messages"][-1].content  # Access the content of the first message in the result
#for j in final_result.stream({"messages":["who is messi?"]}):
 #   for value in j.values():
   #     print(value["messages"][-1].content)  # Print the last message in the stream
