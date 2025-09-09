from sentence_transformers import SentenceTransformer

_model = None

def get_model():
    global _model
    if _model is None:
        # ✅ 384-dim lightweight model
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2")
    return _model

def get_query_embedding(text: str):
    """
    Returns a normalized embedding vector for the given text.
    """
    model = get_model()
    embedding = model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    return embedding.tolist()
