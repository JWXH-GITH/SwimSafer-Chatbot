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

# Lazy model cache
_model_loaded = False

def retrieve_context(state: ChatState) -> ChatState:
    global _model_loaded
    if not _model_loaded:
        # Import heavy models here instead of at startup
        import sentence_transformers  # only when needed
        _model_loaded = True

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
