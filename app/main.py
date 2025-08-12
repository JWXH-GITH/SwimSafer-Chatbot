import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langgraph.graph import StateGraph
from app.graph import build_graph

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_graph()

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    input_data = {"query": request.message}
    result = graph.invoke(input_data)
    return {"response": result.get("response", "Sorry, no response.")}

def main():
    input_data = {"query": "Hello, how can I help you?"}
    result = graph.invoke(input_data)
    print("Response:", result)

if __name__ == "__main__":
    main()
