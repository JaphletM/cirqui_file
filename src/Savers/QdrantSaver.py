from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from Services.EmbeddingService import embed_text
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


def search_similar_terms(query_text, limit=5):
    create_collection_if_not_exists()

    query_embedding = embed_text(query_text)

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=limit,
        with_payload=True
    )

    return results.points


def find_existing_term(term, threshold=0.80):
    results = search_similar_terms(term, limit=1)

    if results and results[0].score >= threshold:
        return results[0].payload

    return None