from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter

# Connect to your local Qdrant (adjust host and port if needed)
client = QdrantClient(host="localhost", port=6333)

# Your collection name
collection_name = "chatbot_docs"

# The query embedding — you need to get this by embedding your query text
# For demonstration, let's say you already have an embedding function `embed_text`
def embed_text(text):
    # Replace this with your real embedding code (e.g. OpenAI or HuggingFace)
    return [0.1] * 1536  # dummy embedding vector

query = "how to get results?"
query_vector = embed_text(query)

# Search for the top 3 most similar chunks
results = client.search(
    collection_name=collection_name,
    query_vector=query_vector,
    limit=3
)

print("Top 3 retrieved chunks:")
for hit in results:
    # Assuming your payload has a 'text' field storing chunk content
    print(f"Score: {hit.score:.4f}, Text: {hit.payload.get('text')}")
