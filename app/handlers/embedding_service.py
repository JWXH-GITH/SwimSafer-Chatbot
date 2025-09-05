# app/handlers/embedding_service.py

import torch
from sentence_transformers import SentenceTransformer

# Load model once globally
_embedding_model = SentenceTransformer("sentence-transformers/paraphrase-MiniLM-L12-v2")

def get_query_embedding(text: str):
    """
    Returns a normalized embedding vector for a given text.
    Optimized for minimal memory usage on Render Free.
    """
    with torch.no_grad():  # prevents building computation graph
        embedding = _embedding_model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        ).astype("float32")  # reduce memory per embedding
    return embedding.tolist()
