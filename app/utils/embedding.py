import os
import psutil
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

_model = None

def print_memory_usage():
    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / (1024 * 1024)
    print(f"[Memory] {mem_mb:.2f} MB used")

def get_embedding_model():
    global _model
    if _model is None:
        print("Loading embedding model...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")  # lightweight & 768-dim
        print("Model loaded.")
        print_memory_usage()
    return _model

def get_query_embedding(text: str):
    model = get_embedding_model()
    embedding = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
    print_memory_usage()
    return embedding.tolist()
