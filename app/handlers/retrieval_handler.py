from app.handlers.embedding_service import get_query_embedding
from qdrant_client import QdrantClient
import os

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    prefer_grpc=False,
    timeout=30,
)

COLLECTION_NAME = "chatbot_docs"

def retrieve_similar(query, top_k=5):
    embedding = get_query_embedding(query)
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=embedding,
        limit=top_k
    )
    return results
