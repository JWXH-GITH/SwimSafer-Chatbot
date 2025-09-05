from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv

load_dotenv()

_model = None

def get_model():
    global _model
    if _model is None:
        # 768-dim model, relatively small
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2")
    return _model

def get_query_embedding(text: str):
    model = get_model()
    embedding = model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    return embedding.tolist()
