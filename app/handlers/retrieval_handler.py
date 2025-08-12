import os
import sys
from dotenv import load_dotenv

# Add the absolute path to the `app` directory
app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
sys.path.insert(0, app_path)

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# --- Load env variables ---
load_dotenv()

# --- Config ---
COLLECTION_NAME = "chatbot_docs"
VECTOR_DIM = 768  # For e5-base-v2

# --- Initialize Qdrant ---
qdrant_url = os.getenv("QDRANT_URL")
if not qdrant_url or "qdrant" not in qdrant_url:
    print("Using fallback Qdrant URL")
    qdrant_url = "https://d2161df3-ff04-4a1e-badf-55a3878d037e.europe-west3-0.gcp.cloud.qdrant.io"

qdrant = QdrantClient(
    url=qdrant_url,
    api_key=os.getenv("QDRANT_API_KEY")
)

# --- Load embedding model once ---
print("Loading embedding model into memory...")
embedding_model = SentenceTransformer("intfloat/e5-base-v2")

# --- Embedding function ---
def get_query_embedding(text: str):
    return embedding_model.encode(text, normalize_embeddings=True).tolist()

# --- Retrieval function ---
def retrieve_similar(query_text, top_k=5, min_score=0.75):
    embedding = get_query_embedding(query_text)

    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=embedding,
        limit=top_k,
        with_payload=True,
        with_vectors=False
    )

    # Only return results above threshold
    return [res for res in results if res.score >= min_score]
