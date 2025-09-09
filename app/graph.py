from app.handlers.retrieval_handler import retrieve_similar
from app.handlers.response_handler import generate_response

def retrieve_context(state):
    query = state["query"]
    results = retrieve_similar(query, top_k=5)
    retrieved_chunks = [hit.payload.get("text", "") for hit in results if "text" in hit.payload]
    state["context"] = "\n\n".join(retrieved_chunks)
    return state

def build_graph():
    # Minimal graph – retrieval then response generation
    def pipeline(state):
        state = retrieve_context(state)
        state = generate_response(state)
        return state
    return pipeline
