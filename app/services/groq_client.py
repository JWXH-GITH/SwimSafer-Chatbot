import os
import requests

class GroqClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.groq.ai/v1"  # replace with Groq's actual API base URL

    def chat_complete(self, model: str, messages: list, temperature: float = 0.7, max_tokens: int = 300):
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # raise error for bad responses
        return response.json()
