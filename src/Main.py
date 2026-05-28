from Extractors.TermComparator import compare_terms
from Readers.PromptReader import PromptReader
from Readers.ConfigReader import ConfigReader
from Readers.HUMIntReader import HumintReader
from LLMclient import LLMClient
from Extractors.TechnicalTermExtractor import extract_technical_terms
from database import load_existing_terms, save_new_terms
from EmbeddingService import embed_term
from QdrantSaver import save_term_embedding


# Load config
config_reader = ConfigReader("data/config/config.txt")
config_reader.read_config()

customer_name = config_reader.get_config("customer_name")
model = config_reader.get_config("model")


# Load prompt template
reader = PromptReader("data/prompts/001-technical-landscape.md")
template = reader.read_prompt()


# Load HUMINT data
humint_reader = HumintReader(
    f"data/humanInt/{customer_name}.md"
)

humint_text = humint_reader.read_humint()

print(humint_text)


# Fill prompt
filled_prompt = template.format(
    CUSTOMER_NAME=customer_name,
    HUMINT_TEXT=humint_text
)

print(filled_prompt)


# Initialize LLM
llm_client = LLMClient(model)


# Generate response
response = llm_client.ask(filled_prompt)

print(response)


# Extract technical terms
extracted_terms = extract_technical_terms(
    response,
    llm_client
)

print(extracted_terms)


# Load existing terms from DB
existing_terms = load_existing_terms()


# Compare extracted terms with existing terms
comparison_results = compare_terms(
    extracted_terms,
    existing_terms
)


# Print comparison results
for result in comparison_results:
    print(result)


# Save new terms
save_new_terms(comparison_results)


# Reload all terms after saving
mongo_terms = load_existing_terms()


# Generate embeddings and save to Qdrant
for term_doc in mongo_terms:
    embedding = embed_term(term_doc)
    save_term_embedding(term_doc, embedding)

    print(f"Saved embedding for: {term_doc.get('term')}")