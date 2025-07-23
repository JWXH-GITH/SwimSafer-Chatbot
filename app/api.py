from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.graph import build_graph

# Request schema
class ChatRequest(BaseModel):
    query: str

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Build LangGraph once
graph = build_graph()

# Define POST endpoint
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    input_data = {"query": request.query}
    result = graph.invoke(input_data)
    return {"response": result["response"]}