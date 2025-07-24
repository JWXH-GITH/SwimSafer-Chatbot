import os
from typing import List, Dict
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI
from tiktoken import encoding_for_model

# Initialize OpenAI client with your API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Constants
MAX_TOKENS = 16385
MODEL_NAME = "gpt-4o"

# --- Token helper functions ---
def num_tokens_from_messages(messages, model=MODEL_NAME):
    enc = encoding_for_model(model)
    tokens_per_message = 4
    tokens_per_name = -1
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(enc.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 2
    return num_tokens

def trim_messages_to_fit_token_limit(messages, max_tokens=MAX_TOKENS):
    system_message = messages[0]
    rest = messages[1:]

    trimmed = []
    for i in range(len(rest)):
        candidate = rest[-(i+1):]
        test_messages = [system_message] + candidate
        if num_tokens_from_messages(test_messages) <= max_tokens:
            trimmed = test_messages
            break
    return trimmed if trimmed else [system_message]

# --- FastAPI app setup ---
class ChatRequest(BaseModel):
    messages: List[Dict]  # Expect list of messages like OpenAI chat format

app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Trim messages to fit token limits
        messages = trim_messages_to_fit_token_limit(request.messages)

        # Make OpenAI chat call
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages
        )

        return {"response": response.choices[0].message.content}

    except Exception as e:
        return {"response": f"Error: {str(e)}"}
