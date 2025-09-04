import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from app.handlers.embedding_service import get_query_embedding  # <-- your function above

# Qdrant setup (reuse same as above)
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    prefer_grpc=False,
    timeout=30,
)

COLLECTION_NAME = "swimsafer-faq"

def retrieve_similar(query: str, top_k: int = 5):
    # 1️⃣ Embed the query
    query_vector = get_query_embedding(query)

    # 2️⃣ Search in Qdrant
    search_result = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k
    )

    # 3️⃣ Return results (mimic old API structure)
    results = []
    for point in search_result:
        # point.payload is a dict containing stored fields (like 'text')
        results.append(point)
    return results
