import os
import sys
import time
import requests
from dotenv import load_dotenv

# Add the absolute path to the `app` directory
app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
sys.path.insert(0, app_path)

from utils.embedding import get_query_embedding
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from qdrant_client.models import Distance, VectorParams

# Load environment variables
load_dotenv()

# Constants
RAW_DIR = "data/raw"
PARSED_DIR = "data/parsed"
COLLECTION_NAME = "chatbot_docs"

# Initialize Qdrant client
qdrant = QdrantClient(url=os.getenv("QDRANT_URL"))

# Create collection if it doesn't exist
if COLLECTION_NAME not in [c.name for c in qdrant.get_collections().collections]:
    qdrant.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
    )

# Function to parse document using LlamaParse API
def parse_document_with_llamaparse(file_path):
    api_key = os.getenv("LLAMAPARSE_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "accept": "application/json"
    }

    # Step 1: Upload file
    with open(file_path, "rb") as f:
        files = {"file": f}
        upload_url = "https://api.cloud.llamaindex.ai/api/v1/parsing/upload"
        upload_response = requests.post(upload_url, headers=headers, files=files)
        upload_response.raise_for_status()
        print("Upload response:", upload_response.json())
        job_id = upload_response.json()["id"]

    # Step 2: Poll for job status
    status_url = f"https://api.cloud.llamaindex.ai/api/v1/parsing/job/{job_id}"
    while True:
        status_response = requests.get(status_url, headers=headers)
        status_response.raise_for_status()
        status_data = status_response.json()
        if status_data["status"] == "completed":
            break
        elif status_data["status"] == "failed":
            raise Exception(f"Parsing job failed for {file_path}")
        time.sleep(2)

    # Step 3: Get Markdown result
    result_url = f"https://api.cloud.llamaindex.ai/api/v1/parsing/job/{job_id}/result/markdown"
    result_response = requests.get(result_url, headers=headers)
    result_response.raise_for_status()
    return result_response.text

# Process each file in RAW_DIR
for filename in os.listdir(RAW_DIR):
    if filename == ".DS_Store":
        continue

    file_path = os.path.join(RAW_DIR, filename)
    print(f"Processing: {filename}")

    try:
        # Parse document
        parsed_text = parse_document_with_llamaparse(file_path)

        # Save parsed text
        parsed_file_path = os.path.join(PARSED_DIR, f"{filename}.txt")
        with open(parsed_file_path, "w", encoding="utf-8") as f:
            f.write(parsed_text)

        # Embed and store in Qdrant
        embedding = get_query_embedding(parsed_text)
        point = PointStruct(id=filename, vector=embedding, payload={"text": parsed_text})
        qdrant.upsert(collection_name=COLLECTION_NAME, points=[point])

        print(f"✓ Successfully ingested: {filename}")

    except Exception as e:
        print(f"✗ Failed to process {filename}: {e}")
