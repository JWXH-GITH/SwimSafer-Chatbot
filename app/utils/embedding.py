import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# --- Config ---
COLLECTION_NAME = "swimsafer-faq"
VECTOR_DIM = 768  # e5-base-v2 output dimension

# --- Qdrant setup ---
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    prefer_grpc=False,
    timeout=30,
)

# --- Load model once (no lazy loading) ---
# Reduce max sequence length to save memory
model = SentenceTransformer(
    "intfloat/e5-base-v2",
    device="cpu"
)
model.max_seq_length = 256  # cut from default 512 → saves memory

# --- Embed Query ---
def get_query_embedding(text: str):
    # Ensure it’s a string (prevent numpy issues)
    text = str(text).strip()
    embedding = model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=True,
        batch_size=1  # keep RAM low
    )
    return embedding.tolist()
