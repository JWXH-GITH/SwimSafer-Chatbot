import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct

from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
load_dotenv()

# --- Config ---
COLLECTION_NAME = "swimsafer-faq"
VECTOR_DIM = 768  # paraphrase-MiniLM-L12-v2 output dimension

# Qdrant setup (remote, not embedded)
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    prefer_grpc=False,
    timeout=30,
)

# Load a lighter Sentence Transformer model
# (fits inside 512MiB Render Free, unlike e5-base-v2)
model = SentenceTransformer("sentence-transformers/paraphrase-MiniLM-L12-v2")

# --- Embed Query ---
def get_query_embedding(text: str):
    embedding = model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    return embedding.tolist()
