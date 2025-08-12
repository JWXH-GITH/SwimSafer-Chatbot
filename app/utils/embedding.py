import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# --- Config ---
COLLECTION_NAME = "chatbot_docs"
VECTOR_DIM = 768  # 768-dim embeddings

# Qdrant setup
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    prefer_grpc=False,
    timeout=30
)

# Load model at startup (avoid lazy loading)
model = SentenceTransformer("intfloat/e5-base-v2")

def get_query_embedding(text: str):
    # No lazy loading, encode immediately
    embedding = model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    return embedding.tolist()
