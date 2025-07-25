import os
import sys
import uuid
import re
from dotenv import load_dotenv

# Add the absolute path to the `app` directory
app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
sys.path.insert(0, app_path)

from app.utils.embedding import get_query_embedding
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, Distance, VectorParams

# Load environment variables
load_dotenv()

# Constants
PARSED_DIR = "data/parsed"
COLLECTION_NAME = "chatbot_docs"
MAIN_FILENAMES = ["Main Faq.txt", "output 5.md"]
VECTOR_DIM = 768  # Updated for e5-base-v2

# Set Qdrant URL with fallback
qdrant_url = os.getenv("QDRANT_URL")
if not qdrant_url or "qdrant" in qdrant_url or qdrant_url.strip() == "":
    print("Using fallback Qdrant URL")
    qdrant_url = "https://f1220f8d-947b-45d6-8b14-9ce454415ca3.eu-west-1-0.aws.cloud.qdrant.io"

# Initialize Qdrant client
qdrant = QdrantClient(
    url=qdrant_url,
    api_key=os.getenv("QDRANT_API_KEY")
)

# Create collection if it does NOT exist
if not qdrant.collection_exists(COLLECTION_NAME):
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE),
    )
else:
    print(f"Collection '{COLLECTION_NAME}' already exists, skipping creation.")

# Chunking functions
def chunk_by_question(text):
    parts = re.split(r'\n(?=Q:)', text)
    return [part.strip() for part in parts if part.strip()]

def generic_chunk(text, max_len=700):
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

# Topic classifier
def classify_topic(text):
    keywords = {
        "registration": [
            "register", "sign up", "account", "login", "create", "email", "dashboard", "profile", "setup", "password"
        ],
        "assessment": [
            "assessment", "slot", "book", "reschedule", "schedule", "test criteria", "practical", "quiz", "stage",
            "level", "assessment centre", "safety briefing", "re-attempt", "results", "certificate", "assessor",
            "submit results"
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
            "assign", "participant tagging", "instructor"
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
        "permit": [
            "usage permit", "swimming pool", "approval", "expired", "renew", "instructor permit", "permit validity"
        ],
        "expiry": [
            "expiry", "validity", "expire", "extension", "instructor expiry", "quiz expiry", "registration expiry"
        ],
        "stages": [
            "stage", "criteria", "level", "stages", "swimsafer stages", "stage criteria", "stage info"
        ],
        "instructor": [
            "instructor", "manual", "course", "certification", "permit", "usage permit", "instructor permit"
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

# Ingest files
def ingest_documents():
    for filename in os.listdir(PARSED_DIR):
        if not filename.endswith(".md") and not filename.endswith(".txt"):
            continue

        file_path = os.path.join(PARSED_DIR, filename)
        print(f"\n📄 Processing: {filename}")

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                parsed_text = f.read()

            category = "main" if filename in MAIN_FILENAMES else "supplement"
            chunks = chunk_by_question(parsed_text) if category == "main" else generic_chunk(parsed_text)

            ingested_count = 0

            for chunk in chunks:
                chunk = chunk.strip()
                if len(chunk) < 20 or len(chunk) > 2000:
                    continue  # skip overly short or long chunks

                embedding = get_query_embedding(chunk)
                if not embedding or len(embedding) != VECTOR_DIM:
                    continue  # skip invalid embeddings

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

# Simple retrieval function
def retrieve_similar(query_text, top_k=5):
    embedding = get_query_embedding(query_text)
    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=embedding,
        limit=top_k,
        with_payload=True
    )
    return results

if __name__ == "__main__":
    ingest_documents()
