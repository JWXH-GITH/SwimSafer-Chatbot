import os
import sys
from dotenv import load_dotenv

# Add the absolute path to the `app` directory
app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
sys.path.insert(0, app_path)

from utils.embedding import get_query_embedding
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct

# Load environment variables
load_dotenv()

# Constants
PARSED_DIR = "data/parsed"
COLLECTION_NAME = "chatbot_docs"

# Initialize Qdrant client
qdrant = QdrantClient(url=os.getenv("QDRANT_URL"))

# Ingest each parsed file
for filename in os.listdir(PARSED_DIR):
    if not filename.endswith(".md") and not filename.endswith(".txt"):
        continue

    file_path = os.path.join(PARSED_DIR, filename)
    print(f"Processing: {filename}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            parsed_text = f.read()

        # Generate embedding
        embedding = get_query_embedding(parsed_text)

        # ✅ Generate valid UUID for Qdrant
        import uuid
        point_id = str(uuid.uuid4())

        # ✅ Create Qdrant point
        point = PointStruct(
            id=point_id,
            vector=embedding,
            payload={"text": parsed_text, "source": filename}
        )

        # ✅ Upsert into Qdrant
        qdrant.upsert(collection_name=COLLECTION_NAME, points=[point])

        print(f"✓ Successfully ingested: {filename}")

    except Exception as e:
        print(f"✗ Failed to process {filename}: {e}")

