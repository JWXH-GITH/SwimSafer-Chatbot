import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from dotenv import load_dotenv

load_dotenv()

def generate_response(prompt: str) -> str:
    """
    Generates a response from OpenAI's GPT-4 model given a prompt.
    """
    response = client.chat.completions.create(model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ])
    return response.choices[0].message.content
