from typing import TypedDict
from langgraph.graph import StateGraph
from app.handlers.query_handler import handle_query
from app.handlers.retrieval_handler import retrieve_similar
from app.handlers.response_handler import generate_response

# Define the state
class ChatState(TypedDict):
    query: str
    context: str
    response: str

# Wrap retrieval into a node that accepts/returns ChatState
def retrieve_context(state: ChatState) -> ChatState:
    query = state["query"]
    results = retrieve_similar(query, top_k=5)
    context = "\n\n".join([hit.payload.get("text", "") for hit in results])
    state["context"] = context
    return state

# Build LangGraph
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
