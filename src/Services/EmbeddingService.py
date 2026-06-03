from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
api_key = os.getenv("OPENAI_API_KEY")
)


def embed_text(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    return response.data[0].embedding


def embed_term(term_doc):
    text = f"{term_doc['term']}: {term_doc.get('definition', '')}"
    return embed_text(text)