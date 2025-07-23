import os
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_query_embedding(text: str) -> list:
    """
    Generates an embedding vector for the given text using OpenAI SDK ≥ 1.0.0.
    """
    response = client.embeddings.create(
        model="text-embedding-3-small",  # You can also use "text-embedding-3-large"
        input=[text]  # Input must be a list of strings
    )
    return response.data[0].embedding
