import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# Lazy-load the model to save memory on startup
_model = None

def get_model():
    global _model
    if _model is None:
        # Revert to e5-base-v2 (768-dim)
        _model = SentenceTransformer("intfloat/e5-base-v2")
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
