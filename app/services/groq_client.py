import os
import requests

class GroqClient:
    def __init__(self, api_key: str, base_url: str = "https://api.groq.com/openai/v1"):
        self.api_key = api_key
        self.base_url = base_url

    def chat_complete(self, model: str, messages: list, temperature: float = 0.7, max_tokens: int = 300):
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Will raise an exception for HTTP errors
        return response.json()