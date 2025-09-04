# app/handlers/embedding_service.py

import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# Load model once
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("intfloat/e5-base-v2")
    return _model

def get_query_embedding(text: str):
    """
    Returns a normalized embedding vector for a given text.
    """
    model = get_model()
    embedding = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
    return embedding.tolist()
