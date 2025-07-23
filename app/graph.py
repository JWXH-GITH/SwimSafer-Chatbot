from typing import TypedDict
from langgraph.graph import StateGraph
from app.handlers.query_handler import handle_query
from app.handlers.retrieval_handler import retrieve_context
from app.handlers.response_handler import generate_response

# Define the state using TypedDict
class ChatState(TypedDict):
    query: str
    context: str
    response: str

# Build the LangGraph
def build_graph():
    graph = StateGraph(ChatState)

    graph.add_node("query", handle_query)
    graph.add_node("retrieve", retrieve_context)
    graph.add_node("respond", generate_response)

    graph.set_entry_point("query")
    graph.add_edge("query", "retrieve")
    graph.add_edge("retrieve", "respond")
    graph.set_finish_point("respond")

    return graph.compile()
