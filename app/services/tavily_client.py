import os
import requests
from dotenv import load_dotenv

load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

def search_web(query: str) -> list:
    """
    Searches the web using Tavily API and returns a list of search results.
    """
    url = "https://api.tavily.com/search"
    headers = {"Authorization": f"Bearer {TAVILY_API_KEY}"}
    payload = {
        "query": query,
        "max_results": 5
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json().get("results", [])
