import os
from qdrant_client import QdrantClient
from app.utils.embedding_service import get_query_embedding

# Connect to Qdrant
client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))
COLLECTION_NAME = "chatbot_docs"

def retrieve_similar(query: str, top_k: int = 5):
    """
    Retrieves the top_k most similar chunks from Qdrant for a given query.
    """
    query_vector = get_query_embedding(query)

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k
    )
    return results
