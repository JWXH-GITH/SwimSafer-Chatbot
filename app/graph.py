from typing import TypedDict
from langgraph.graph import StateGraph

# Define the state
class ChatState(TypedDict):
    query: str
    context: str
    response: str

# Lazy globals for heavy imports
_retrieval_model = None
_response_model = None

# ----------------------------
# Retrieval node (lazy load)
# ----------------------------
def retrieve_context(state: ChatState) -> ChatState:
    global _retrieval_model
    if _retrieval_model is None:
        # Only import when first needed
        from app.handlers.retrieval_handler import retrieve_similar
        _retrieval_model = retrieve_similar

    query = state["query"]
    results = _retrieval_model(query, top_k=5)
    state["context"] = "\n\n".join([hit.payload.get("text", "") for hit in results])
    return state

# ----------------------------
# Response node (lazy load)
# ----------------------------
def generate_response_node(state: ChatState) -> ChatState:
    global _response_model
    if _response_model is None:
        from app.handlers.response_handler import generate_response
        _response_model = generate_response

    state["response"] = _response_model(state)
    return state

# ----------------------------
# Query node (light)
# ----------------------------
def handle_query_node(state: ChatState) -> ChatState:
    from app.handlers.query_handler import handle_query
    state = handle_query(state)  # ✅ Pass state to handle_query
    return state

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
