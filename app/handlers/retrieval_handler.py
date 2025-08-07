import os
import sys
from dotenv import load_dotenv

# Add the absolute path to the `app` directory
app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
sys.path.insert(0, app_path)

from app.utils.embedding import get_query_embedding
from qdrant_client import QdrantClient

# Load environment variables
load_dotenv()

# Constants
COLLECTION_NAME = "chatbot_docs"
VECTOR_DIM = 768  # For e5-base-v2

# Setup Qdrant URL
qdrant_url = os.getenv("QDRANT_URL")
if not qdrant_url or "qdrant" not in qdrant_url:
    print("⚠️  Using fallback Qdrant URL")
    qdrant_url = "https://d2161df3-ff04-4a1e-badf-55a3878d037e.europe-west3-0.gcp.cloud.qdrant.io"

# Initialize Qdrant client with optimized settings
qdrant = QdrantClient(
    url=qdrant_url,
    api_key=os.getenv("QDRANT_API_KEY"),
    prefer_grpc=False,
    timeout=20,  # Reduce timeout to avoid long hangs
)

def retrieve_similar(query_text, top_k=5, min_score=0.75):
    """Retrieve top-k relevant chunks for a given query based on vector similarity."""
    embedding = get_query_embedding(query_text)

    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=embedding,
        limit=top_k,
        with_payload=True,
        with_vectors=False,
    )

    return [res for res in results if res.score >= min_score]
