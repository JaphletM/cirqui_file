from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
import uuid


client = QdrantClient(
    host="localhost",
    port=6333
)

COLLECTION_NAME = "technical_knowledge"

def create_collection_if_not_exists():
    collection_names = [
        collection.name
        for collection in client.get_collections().collections
    ]

    if COLLECTION_NAME not in collection_names:
        print(f"Creating Qdrant collection: {COLLECTION_NAME}")

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=1536,
                distance=Distance.COSINE
            )
        )

def save_term_embedding(term_doc, embedding):

    create_collection_if_not_exists()

    point = PointStruct(
        id=str(term_doc.get("_id", uuid.uuid4())),
        vector=embedding,
        payload={
            "term": term_doc["term"],
            "definition": term_doc.get("definition", "")
        }
    )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[point]
    )

    point = PointStruct(
        id=str(term_doc.get("_id", uuid.uuid4())),
        vector=embedding,
        payload={
            "term": term_doc["term"],
            "definition": term_doc.get("definition", "")
        }
    )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[point]
    )