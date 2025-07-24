import os
import sys
import uuid
import re
from dotenv import load_dotenv

# Add the absolute path to the `app` directory
app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
sys.path.insert(0, app_path)

from utils.embedding import get_query_embedding
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, Distance, VectorParams

# Load environment variables
load_dotenv()

# Constants
PARSED_DIR = "data/parsed"
COLLECTION_NAME = "chatbot_docs"
MAIN_FILENAME = "Main Faq.txt"

# Set Qdrant URL with fallback
qdrant_url = os.getenv("QDRANT_URL")
if not qdrant_url or "qdrant" in qdrant_url or qdrant_url.strip() == "":
    print("Using fallback Qdrant URL")
    qdrant_url = "http://localhost:6333"

# Initialize Qdrant client
qdrant = QdrantClient(url=qdrant_url)

# Recreate collection
if qdrant.collection_exists(COLLECTION_NAME):
    qdrant.delete_collection(COLLECTION_NAME)

qdrant.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
)

# Split main FAQ files by numbered question (e.g. 1. What is...)
def chunk_by_question(text):
    chunks = re.split(r"\n(?=\d+\.\s)", text)
    return [chunk.strip() for chunk in chunks if chunk.strip()]

# Generic sentence-based chunking for other text files
def generic_chunk(text, max_len=500):
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunk = ""
    chunks = []
    for sentence in sentences:
        if len(chunk) + len(sentence) < max_len:
            chunk += " " + sentence
        else:
            chunks.append(chunk.strip())
            chunk = sentence
    if chunk:
        chunks.append(chunk.strip())
    return chunks

# Enhanced topic classifier
def classify_topic(text):
    keywords = {
        "registration": [
            "register", "sign up", "account", "login", "create", "email", "dashboard", "profile", "setup", "password"
        ],
        "assessment": [
            "assessment", "slot", "book", "reschedule", "schedule", "test criteria", "practical", "quiz", "stage", 
            "level", "assessment centre", "safety briefing", "re-attempt", "results", "certificate"
        ],
        "appeal": [
            "appeal", "not competent", "reassess", "re-evaluate", "disagree", "conflict of interest", "panel", 
            "submit reason", "refund", "non competent", "failed"
        ],
        "results": [
            "results", "certificates", "pass", "fail", "check results", "status", "green check", "download", 
            "quiz score", "completion", "view results"
        ],
        "payment": [
            "payment", "invoice", "cart", "fee", "cost", "transaction", "checkout", "total amount", "proceed to payment"
        ],
        "coach": [
            "coach", "validate", "linked participants", "club", "freelance", "unattached", "role", "dashboard", 
            "assign", "participant tagging"
        ],
        "participant": [
            "participant", "tag", "link", "select coach", "club affiliation", "profile", "NRIC", "personal information"
        ],
        "rescheduling": [
            "reschedule", "change slot", "inclement weather", "rain-off", "deadline", "medical certificate", 
            "absence", "cancel", "no-show"
        ],
        "quiz": [
            "online theory quiz", "quiz", "score", "attempt", "extension", "pass rate", "deadline", "expiry", 
            "complete quiz"
        ],
        "certificate": [
            "certificate", "retrieve", "download", "completion", "stage", "profile", "CAMs platform"
        ],
        "medical": [
            "medical", "doctor", "memo", "condition", "certificate", "permanent", "temporary", "review", "submit"
        ],
        "technical": [
            "platform", "CAMS", "system", "login issues", "confirmation email", "technical difficulties", 
            "support", "contact"
        ],
        "general": [
            "swim safer", "safety", "programme", "user manual", "overview", "introduction", "terms and conditions"
        ]
    }

    text_lower = text.lower()
    for topic, words in keywords.items():
        if any(word in text_lower for word in words):
            return topic
    return "general"

# Ingest each file
for filename in os.listdir(PARSED_DIR):
    if not filename.endswith(".md") and not filename.endswith(".txt"):
        continue

    file_path = os.path.join(PARSED_DIR, filename)
    print(f"\n📄 Processing: {filename}")

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            parsed_text = f.read()

        category = "main" if filename == MAIN_FILENAME else "supplement"
        chunks = chunk_by_question(parsed_text) if category == "main" else generic_chunk(parsed_text)

        ingested_count = 0

        for chunk in chunks:
            if len(chunk.strip()) < 20 or len(chunk) > 2000:
                continue  # skip overly short or long chunks

            embedding = get_query_embedding(chunk)
            topic = classify_topic(chunk)
            point_id = str(uuid.uuid4())

            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "text": chunk,
                    "source": filename,
                    "category": category,
                    "topic": topic
                }
            )

            qdrant.upsert(collection_name=COLLECTION_NAME, points=[point])
            ingested_count += 1

        print(f"✅ Ingested {ingested_count} chunks from '{filename}' as category: {category}")

    except Exception as e:
        print(f"❌ Failed to process '{filename}': {e}")
