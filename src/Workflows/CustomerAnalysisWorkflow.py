from Extractors.TermComparator import compare_terms
from Readers.PromptReader import read_prompts
from Readers.ConfigReader import ConfigReader
from Readers.HUMIntReader import HumintReader
from SaversJson.MongoJsonSaver import append_to_mongo_json, read_mongo_json_safe
from Services.LLMclient import LLMClient
from Extractors.TechnicalTermExtractor import extract_technical_terms
#from Savers.MongoSaver import load_existing_terms, save_new_terms
from Services.EmbeddingService import embed_term
#from Savers.QdrantSaver import save_term_embedding
#from Savers.QdrantSaver import find_existing_term


def run_customer_analysis_workflow():

    # Read customer-specific settings
    customer_name, model = load_config()

    # Initialize LLM connection
    llm_client = LLMClient(model)

    # Load workflow prompts
    technical_landscape_prompt, extract_terms_prompt, followup_prompts_prompt = load_prompts()

    # Read HUMINT notes for the customer
    humint_text = load_humint(customer_name)

    # Generate an overview of the customer's technical landscape
    technical_landscape_response = generate_technical_landscape(
        technical_landscape_prompt,
        customer_name,
        humint_text,
        llm_client
    )

    # Extract relevant technologies and technical concepts
    extracted_terms = extract_terms(
        technical_landscape_response,
        llm_client,
        extract_terms_prompt
    )

    # Check which terms already exist in the knowledge base
    comparison_results = compare_terms_with_database(
        extracted_terms
    )

    # Print results to verify term matching
    print_comparison_results(comparison_results)

   # check_terms_in_vector_store(comparison_results)

    followup_prompts = generate_followup_prompts(
        comparison_results,
        llm_client,
        followup_prompts_prompt
    )

    print(followup_prompts)

    # Store new terms in MongoDB
    save_terms(comparison_results)

    # Create embeddings and push them to Qdrant
    #generate_and_save_embeddings()


def load_config():
    config_reader = ConfigReader("data/config/config.txt")
    config_reader.read_config()

    customer_name = config_reader.get_config("customer_name")
    model = config_reader.get_config("model")

    return customer_name, model


def load_prompts():
    prompt_templates = read_prompts("data/prompts")

    technical_landscape_prompt = prompt_templates[0]
    extract_terms_prompt = prompt_templates[1]
    generate_followup_prompts = prompt_templates[2]

    return (
        technical_landscape_prompt,
        extract_terms_prompt,
        generate_followup_prompts
    )


def load_humint(customer_name):
    humint_reader = HumintReader(
        f"data/humanInt/{customer_name}.md"
    )

    return humint_reader.read_humint()


def generate_technical_landscape(
    technical_landscape_prompt,
    customer_name,
    humint_text,
    llm_client
):
    filled_prompt = technical_landscape_prompt.format(
        CUSTOMER_NAME=customer_name,
        HUMINT_TEXT=humint_text
    )

    return llm_client.ask(filled_prompt)


def extract_terms(
    technical_landscape_response,
    llm_client,
    extract_terms_prompt
):
    return extract_technical_terms(
        technical_landscape_response,
        llm_client,
        extract_terms_prompt
    )

def compare_terms_with_database(extracted_terms):
    existing_terms = read_mongo_json_safe()

    return compare_terms(
        extracted_terms,
        existing_terms
    )



#def compare_terms_with_database(extracted_terms):
    existing_terms = load_existing_terms()

    return compare_terms(
        extracted_terms,
        existing_terms
    )


def print_comparison_results(comparison_results):
    for result in comparison_results:
        print(result)

def save_terms(comparison_results):
    append_to_mongo_json(comparison_results)
    



#def save_terms(comparison_results):
#    save_new_terms(comparison_results)


#def generate_and_save_embeddings():
#    mongo_terms = load_existing_terms()

#    for term_doc in mongo_terms:
#        embedding = embed_term(term_doc)
#        save_term_embedding(term_doc, embedding)

#        print(f"Saved embedding for: {term_doc.get('term')}")

#def check_terms_in_vector_store(comparison_results):
#    for result in comparison_results:
#        term = result.get("term")

#        if not term:
#            continue

#        existing_info = find_existing_term(term)

#        if existing_info:
#            print(f"Found existing semantic knowledge for: {term}")
#            print(existing_info)
#        else:
#            print(f"No semantic knowledge found for: {term}") 

            
def generate_followup_prompts(
    comparison_results,
    llm_client,
    followup_prompts_prompt
):
    technical_terms = []

    for result in comparison_results:
        term = result.get("term")

        if term:
            technical_terms.append(term)

    terms_text = "\n".join(
        f"- {term}"
        for term in technical_terms
    )

    filled_prompt = followup_prompts_prompt.format(
        TECHNICAL_TERMS=terms_text
    )

    response = llm_client.ask(
        filled_prompt
    )

    return response