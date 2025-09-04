# app/handlers/retrieval_handler.py
import os
from dotenv import load_dotenv
from app.services.groq_client import GroqClient

load_dotenv()

_client = None

def get_client():
    """Lazy-load GroqClient to save memory."""
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not set in environment variables")
        _client = GroqClient(api_key=api_key)
    return _client


def retrieve_similar(query: str, top_k: int = 5):
    """
    Retrieves the top_k most similar chunks for a given query
    using Groq vector embeddings.
    """
    client = get_client()

    # Generate query embedding
    embedding_response = client.embed(
        model="llama3-8b-8192",  # or any Groq embedding model
        input=query
    )
    query_embedding = embedding_response["embedding"]

    # Perform similarity search in your Groq index
    search_results = client.similarity_search(
        index_name="swimsafer_chunks",  # your pre-built index
        query_embedding=query_embedding,
        top_k=top_k
    )

    # Each result contains a payload with your stored text
    # Example: {"payload": {"text": "Some SwimSafer info"}, "score": 0.87}
    return search_results
