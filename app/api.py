from typing import List, Dict
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.graph import build_graph
from tiktoken import encoding_for_model

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

class ChatRequest(BaseModel):
    messages: List[Dict]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_graph()  # this returns our pipeline function

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    messages = request.messages
    messages = trim_messages_to_fit_token_limit(messages)
    input_data = {"query": messages[-1]["content"]}
    
    # ✅ call pipeline function directly
    result = graph(input_data)

    return {"response": result["response"]}
