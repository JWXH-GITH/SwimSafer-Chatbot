\import os
import psutil
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

def print_memory_usage(stage=""):
    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / (1024 * 1024)
    print(f"[Memory] {stage}: {mem_mb:.2f} MB used")

print_memory_usage("Before loading embedding model")

# Eagerly load the embedding model at startup
model = SentenceTransformer("all-MiniLM-L6-v2")  # lightweight & 768-dim

print_memory_usage("After loading embedding model")

def get_query_embedding(text: str):
    embedding = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
    print_memory_usage("After embedding a query")
    return embedding.tolist()
