import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# Lazy-load the model to save memory
_model = None

def get_model():
    global _model
    if _model is None:
        # Use a lighter 768-dim model
        _model = SentenceTransformer("sentence-transformers/paraphrase-mpnet-base-v2")
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
