import openai
from typing import List, Dict
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.graph import build_graph
from tiktoken import encoding_for_model

# Helper functions (paste these here or import from utils)
MAX_TOKENS = 16385
MODEL_NAME = "gpt-4o"

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

# Request schema
class ChatRequest(BaseModel):
    messages: List[Dict]  # Expect list of messages like OpenAI chat format

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Build LangGraph once
graph = build_graph()

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    messages = request.messages  # list of dicts like {"role": "...", "content": "..."}

    # trim if needed
    messages = trim_messages_to_fit_token_limit(messages)

    # pass last user message content as query string to your graph

openai.api_key = os.getenv("OPENAI_API_KEY")  # put in .env

response = openai.ChatCompletion.create(
    model=MODEL_NAME,
    messages=messages,
)

return {"response": response.choices[0].message["content"]}
