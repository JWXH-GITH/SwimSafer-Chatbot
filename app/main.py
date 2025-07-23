import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langgraph.graph import StateGraph
from app.graph import build_graph

# Load environment variables
load_dotenv()

# Optional: Print loaded keys for debugging
print("OpenAI Key:", os.getenv("OPENAI_API_KEY"))
print("Qdrant URL:", os.getenv("QDRANT_URL"))

# Initialize FastAPI app
app = FastAPI()

# Allow frontend to access backend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Build LangGraph workflow once
graph = build_graph()

# Request model
class ChatRequest(BaseModel):
    message: str

# Chat endpoint
@app.post("/chat")
async def chat(request: ChatRequest):
    input_data = {"query": request.message}
    result = graph.invoke(input_data)
    return {"response": result.get("response", "Sorry, no response.")}

# Optional: CLI entry point for testing
def main():
    input_data = {"query": "Hello, how can I help you?"}
    result = graph.invoke(input_data)
    print("Response:", result)

if __name__ == "__main__":
    main()