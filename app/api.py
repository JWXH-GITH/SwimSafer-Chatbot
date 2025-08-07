from typing import List, Dict
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import tiktoken

# Constants
MAX_TOKENS = 16385
MODEL_NAME = "gpt-4o"

# -- Helper Functions --

def num_tokens_from_messages(messages, model=MODEL_NAME):
    enc = tiktoken.encoding_for_model(model)
    tokens_per_message = 4  # OpenAI chat format overhead
    tokens_per_name = -1
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(enc.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    return num_tokens + 2  # bias for reply structure

def trim_messages_to_fit_token_limit(messages, max_tokens=MAX_TOKENS):
    if not messages:
        return []
    system_message = messages[0]
    rest = messages[1:]

    for i in range(len(rest)):
        candidate = rest[-(i + 1):]
        test_messages = [system_message] + candidate
        if num_tokens_from_messages(test_messages) <= max_tokens:
            return test_messages
    return [system_message]

# -- Request Schema --

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]

# -- FastAPI App --

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -- Import LangGraph builder only when used --
# To avoid memory usage at boot time
from app.graph import build_graph
graph = build_graph()

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    messages = trim_messages_to_fit_token_limit(request.messages)
    user_query = messages[-1]["content"] if messages else ""

    result = graph.invoke({"query": user_query})
    return {"response": result["response"]}
