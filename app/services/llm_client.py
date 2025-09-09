import os
from app.services.groq_client import GroqClient

# Pick a valid Groq-hosted model
MODEL_NAME = "llama3-8b-8192"

# Initialize Groq client with API key from .env
client = GroqClient(api_key=os.getenv("GROQ_API_KEY"))

def llm_complete(system_prompt: str, user_prompt: str) -> str:
    """
    Sends system + user prompt to Groq LLM and returns the generated answer.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    try:
        response = client.chat_complete(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"❌ LLM error: {e}")
        return "Sorry, I cannot answer that right now."
