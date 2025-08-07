# embedding.py

import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# --- Config ---
COLLECTION_NAME = "swimsafer-faq"
VECTOR_DIM = 768  # e5-base-v2 output dimension

# Qdrant setup
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    prefer_grpc=False,
    timeout=30,
)

# --- Model Loading ---
_model = None  # Internal singleton

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("intfloat/e5-base-v2")
    return _model

# --- Embed Query ---
def get_query_embedding(text: str):
    model = get_model()
    embedding = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
    return embedding.tolist()
