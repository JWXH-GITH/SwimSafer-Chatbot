import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, SearchRequest
from app.utils.embedding import get_query_embedding

# Initialize Qdrant client
qdrant = QdrantClient(url=os.getenv("QDRANT_URL"))

def retrieve_context(state):
    query = state["query"]
    query_vector = get_query_embedding(query)

    search_results = qdrant.search(
        collection_name="chatbot_docs",
        query_vector=query_vector,
        limit=5
    )

    if not search_results:
        return {
            **state,
            "context": ""
        }

    # Optional: filter by score
    filtered_hits = search_results
    context = "\n".join([hit.payload.get("text", "") for hit in filtered_hits])

    return {
        **state,
        "context": context
    }
