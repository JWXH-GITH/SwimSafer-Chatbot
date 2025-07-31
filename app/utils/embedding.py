import os
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
load_dotenv()

# --- Config ---
COLLECTION_NAME = "swimsafer-faq"
VECTOR_DIM = 384  # e5-small-v2 output

# Qdrant setup
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    prefer_grpc=True,
    timeout=30,
)

# Load Sentence Transformer model (faster)
model = SentenceTransformer("intfloat/e5-small-v2")
_ = model.encode("warmup", convert_to_numpy=True, normalize_embeddings=True)

# --- Embed Query ---
def get_query_embedding(text: str):
    embedding = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
    return embedding.tolist()
