import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct

# Load environment variables
load_dotenv()

# Initialize Qdrant client
qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)
def upsert_point(collection_name, id, embedding, payload):
    """
    Upserts a single point into the specified Qdrant collection.
    """
    point = PointStruct(id=id, vector=embedding, payload=payload)
    qdrant.upsert(collection_name=collection_name, points=[point])
