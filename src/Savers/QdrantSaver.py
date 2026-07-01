import re

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from Services.EmbeddingService import embed_text
import uuid


client = QdrantClient(
    host="localhost",
    port=6333
)

COLLECTION_NAME = "technical_knowledge"
RAPPORT_COLLECTION_NAME = "company_rapports"


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


def create_rapport_collection_if_not_exists():
    collection_names = [
        collection.name
        for collection in client.get_collections().collections
    ]

    if RAPPORT_COLLECTION_NAME not in collection_names:
        print(f"Creating Qdrant collection: {RAPPORT_COLLECTION_NAME}")

        client.create_collection(
            collection_name=RAPPORT_COLLECTION_NAME,
            vectors_config=VectorParams(
                size=1536,
                distance=Distance.COSINE
            )
        )


def split_rapport_into_sections(rapport_text):
    sections = []
    matches = list(re.finditer(r"^##\s+(.+)$", rapport_text, flags=re.MULTILINE))

    if not matches:
        return [("Rapport", rapport_text.strip())]

    for index, match in enumerate(matches):
        section_title = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(rapport_text)
        section_text = rapport_text[start:end].strip()
        sections.append((section_title, section_text))

    return sections


def save_rapport_embedding(company_name, rapport_text):
    create_rapport_collection_if_not_exists()

    sections = split_rapport_into_sections(rapport_text)

    for section_title, section_text in sections:
        embedding = embed_text(section_text)

        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "company": company_name,
                "section": section_title,
                "text": section_text
            }
        )

        client.upsert(
            collection_name=RAPPORT_COLLECTION_NAME,
            points=[point]
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


def find_existing_term(term, definition="", threshold=0.80):
    query = f"{term}: {definition}" if definition else term
    results = search_similar_terms(query, limit=1)

    if results and results[0].score >= threshold:
        return results[0].payload

    return None