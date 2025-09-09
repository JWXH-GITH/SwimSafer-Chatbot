# app/services/llm_client.py
import os
import requests

from app.services.groq_client import GroqClient

# Initialize Groq client with API key from Render environment
groq = GroqClient(api_key=os.getenv("GROQ_API_KEY"))

# Pick a valid Groq-hosted model
MODEL_NAME = "llama-3.1-8b-instant"  # adjust if needed

def llm_complete(system_prompt: str, user_prompt: str, max_tokens: int = 300, temperature: float = 0.7) -> str:
    """
    Sends system + user prompt to Groq LLM and returns the generated answer.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        response = groq.chat_complete(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        # Extract content safely
        choices = response.get("choices", [])
        if not choices:
            return "Sorry, I cannot answer that right now."
        message = choices[0].get("message", {})
        return message.get("content", "Sorry, I cannot answer that right now.").strip()
    except Exception as e:
        print(f"❌ LLM error: {e}")
        return "Sorry, I cannot answer that right now."
