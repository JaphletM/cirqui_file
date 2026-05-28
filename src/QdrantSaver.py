from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct


client = QdrantClient(
    host="localhost",
    port=6333
)

COLLECTION_NAME = "technical_knowledge"


def save_term_embedding(term_doc, embedding):

    point = PointStruct(
        id=str(term_doc["_id"]),
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