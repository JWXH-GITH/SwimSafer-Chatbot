from typing import TypedDict
from langgraph.graph import StateGraph

# Define the shared state
class ChatState(TypedDict):
    query: str
    context: str
    response: str

# ----------------------------
# Lazy globals for heavy imports
# ----------------------------
_retrieval_fn = None
_response_fn = None
_query_fn = None

# ----------------------------
# Retrieval node (lazy load)
# ----------------------------
def retrieve_context(state: ChatState) -> ChatState:
    global _retrieval_fn
    if _retrieval_fn is None:
        from app.handlers.retrieval_handler import retrieve_similar
        _retrieval_fn = retrieve_similar

    query = state["query"]
    results = _retrieval_fn(query, top_k=5)
    state["context"] = "\n\n".join([hit.payload.get("text", "") for hit in results if "text" in hit.payload])
    return state

# ----------------------------
# Response node (lazy load)
# ----------------------------
def generate_response_node(state: ChatState) -> ChatState:
    global _response_fn
    if _response_fn is None:
        from app.handlers.response_handler import generate_response
        _response_fn = generate_response

    return _response_fn(state)

# ----------------------------
# Query node (light)
# ----------------------------
def handle_query_node(state: ChatState) -> ChatState:
    global _query_fn
    if _query_fn is None:
        from app.handlers.query_handler import handle_query
        _query_fn = handle_query

    # Pass the state properly
    return _query_fn(state)

# ----------------------------
# Build LangGraph lazily
# ----------------------------
def build_graph():
    graph = StateGraph(ChatState)

    graph.add_node("query", handle_query_node)
    graph.add_node("retrieve", retrieve_context)
    graph.add_node("respond", generate_response_node)

    graph.set_entry_point("query")
    graph.add_edge("query", "retrieve")
    graph.add_edge("retrieve", "respond")
    graph.set_finish_point("respond")

    return graph.compile()
