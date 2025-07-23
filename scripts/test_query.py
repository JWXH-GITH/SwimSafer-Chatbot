import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.utils.embedding import get_query_embedding
from app.services.qdrant_client import qdrant  # or a retrieval function
from app.services.openai_client import generate_response
from app.services.tavily_client import search_web
from app.utils.logging import logger

# Load environment variables
load_dotenv()

COLLECTION_NAME = "your_collection_name"

def test_query(user_query: str):
    logger.info(f"User query: {user_query}")

    # Step 1: Embed query
    query_embedding = get_query_embedding(user_query)

    # Step 2: Retrieve from Qdrant
    search_result = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        limit=3
    )
    retrieved_texts = [hit.payload["text"] for hit in search_result]

    # Step 3: Web search (optional)
    web_results = search_web(user_query)
    web_snippets = [result["content"] for result in web_results]

    # Step 4: Generate response
    context = "\n\n".join(retrieved_texts + web_snippets)
    prompt = f"Answer the following question using the context below:\n\nContext:\n{context}\n\nQuestion: {user_query}"
    response = generate_response(prompt)

    logger.info(f"Response:\n{response}")

if __name__ == "__main__":
    test_query("What is LangGraph and how does it work?")
