from Extractors.TermComparator import compare_terms
from Readers.PromptReader import read_prompts
from Readers.ConfigReader import ConfigReader
from Readers.HUMIntReader import HumintReader
from LLMclient import LLMClient
from Extractors.TechnicalTermExtractor import extract_technical_terms
from Savers.MongoSaver import load_existing_terms, save_new_terms
from EmbeddingService import embed_term
from Savers.QdrantSaver import save_term_embedding


# Load config
config_reader = ConfigReader("data/config/config.txt")
config_reader.read_config()

customer_name = config_reader.get_config("customer_name")
model = config_reader.get_config("model")


# Initialize LLM
llm_client = LLMClient(model)


# Load prompts
prompt_templates = read_prompts("data/prompts")

technical_landscape_prompt = prompt_templates[0]
extract_terms_prompt = prompt_templates[1]


# Load HUMINT data
humint_reader = HumintReader(
    f"data/humanInt/{customer_name}.md"
)

humint_text = humint_reader.read_humint()

print(humint_text)


# Fill technical landscape prompt
filled_prompt = technical_landscape_prompt.format(
    CUSTOMER_NAME=customer_name,
    HUMINT_TEXT=humint_text
)

print(filled_prompt)


# Generate technical landscape response
response = llm_client.ask(filled_prompt)

print(response)


# Extract technical terms from response
extracted_terms = extract_technical_terms(
    response,
    llm_client,
    extract_terms_prompt
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