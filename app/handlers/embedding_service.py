import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# Lazy-load model to save memory
_model = None

def get_model():
    global _model
    if _model is None:
        # Lightweight 768-dim model under 300MB
        _model = SentenceTransformer("sentence-transformers/paraphrase-MiniLM-L12-v2")
    return _model

def get_query_embedding(text: str):
    """
    Returns a normalized embedding vector for a given text.
    """
    model = get_model()
    embedding = model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    return embedding.tolist()
