import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.embedding import get_query_embedding

def test_embedding():
    text = "Hello, how does the SwimSafer program work?"
    embedding = get_query_embedding(text)
    print(f"Embedding dimension: {len(embedding)}")  # Should print 1536
    print(f"Sample values (first 10): {embedding[:10]}")

if __name__ == "__main__":
    test_embedding()
