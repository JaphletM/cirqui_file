import json
from bleach import clean

from Extractors.TermComparator import compare_terms
from Readers.PromptReader import read_prompts
from Readers.ConfigReader import ConfigReader
from Readers.HUMIntReader import HumintReader
from Services.LLMclient import LLMClient
from Extractors.TechnicalTermExtractor import extract_technical_terms
from Savers.MongoSaver import load_existing_terms, save_new_terms
from Services.EmbeddingService import embed_term
from Savers.QdrantSaver import save_term_embedding
from Savers.QdrantSaver import find_existing_term
from Savers.QdrantSaver import save_rapport_embedding
from Savers.JsonSaver import save_to_json, save_webint
from Savers.MarkdownSaver import save_to_markdown


def run_customer_analysis_workflow(customer_name: str = None, llm_client=None):
    customer_name = resolve_customer_name(customer_name)
    llm_client = resolve_llm_client(llm_client)

    print(f"\nCIRQUI start analyse voor: {customer_name}")
    print("─" * 40)

    prompts = load_prompts()

    print("📄 HUMINT wordt ingeladen...")
    humint_text = load_humint(customer_name)

    print("🌐 Technisch landschap wordt gegenereerd via Gemini...")
    landscape_request = {
        "prompt_template": prompts["technical_landscape"],
        "customer_name": customer_name,
        "humint_text": humint_text
    }
    technical_landscape_response = generate_technical_landscape(landscape_request, llm_client)
    save_webint(customer_name, technical_landscape_response)
    print("✓ Technisch landschap opgeslagen.")

    print("\n🔍 Technische termen worden geëxtraheerd...")
    terms_request = {"text": technical_landscape_response, "prompt_template": prompts["extract_terms"]}
    extracted_terms = extract_technical_terms(terms_request, llm_client)
    print(f"✓ {len(extracted_terms)} termen gevonden.")

    print("\n🗄️  Termen worden vergeleken met database...")
    comparison_results = compare_terms_with_database(extracted_terms)

    check_terms_in_vector_store(comparison_results)

    new_terms_for_followup = find_new_terms(comparison_results)
    print(f"✓ {len(new_terms_for_followup)} nieuwe termen gevonden.")

    print("\n💬 Vervolgvragen worden gegenereerd en beantwoord...")
    followup_request = {
        "comparison_results": comparison_results,
        "new_terms": new_terms_for_followup,
        "followup_prompts_prompt": prompts["followup_prompts"],
        "answer_followup_questions_prompt": prompts["answer_followup_questions"],
        "generate_rapports_prompt": prompts["generate_rapports"],
        "humint_text": humint_text,
        "customer_name": customer_name
    }
    followup_prompts, answer_response, rapport = generate_followup_prompts(followup_request, llm_client)

    merge_request = {
        "followup_prompts": followup_prompts,
        "answer_response": answer_response,
        "comparison_results": comparison_results
    }
    merged = merge_followup_data(merge_request)

    print("\n📊 Analyse wordt opgeslagen...")
    save_to_json(customer_name, merged)
    print("✓ Analyse opgeslagen.")

    print("\n📝 Rapport wordt opgesteld...")
    save_to_markdown(customer_name, rapport)
    print("✓ Rapport opgeslagen.")
    save_rapport_embedding(customer_name, rapport)

    print("\n💾 Nieuwe termen worden opgeslagen in database...")
    save_terms(comparison_results, customer_name)

    print("\n🧠 Embeddings worden gegenereerd en opgeslagen...")
    generate_and_save_embeddings(new_terms_for_followup)

    print("\n" + "─" * 40)
    print(f"✅ Analyse voor {customer_name} voltooid!")


def resolve_customer_name(customer_name):
    if customer_name:
        return customer_name

    return input("Voer de naam van de klant in: ")


def resolve_llm_client(llm_client):
    if llm_client:
        return llm_client

    model = load_config()
    return LLMClient(model)


def load_config():
    config_reader = ConfigReader("data/config/config.txt")
    config_reader.read_config()
    return config_reader.get_config("model")


def load_prompts():
    prompt_templates = read_prompts("data/prompts")

    return {
        "technical_landscape": prompt_templates[0],
        "extract_terms": prompt_templates[1],
        "followup_prompts": prompt_templates[2],
        "answer_followup_questions": prompt_templates[3],
        "generate_rapports": prompt_templates[4]
    }


def load_humint(customer_name):
    humint_reader = HumintReader(f"data/humanInt/{customer_name}.md")
    return humint_reader.read_humint()


def generate_technical_landscape(request: dict, llm_client) -> str:
    filled_prompt = request["prompt_template"].format(
        CUSTOMER_NAME=request["customer_name"],
        HUMINT_TEXT=request["humint_text"]
    )
    return llm_client.ask(filled_prompt)


def compare_terms_with_database(extracted_terms):
    existing_terms = load_existing_terms()
    return compare_terms(extracted_terms, existing_terms)


def find_new_terms(comparison_results: list) -> list:
    return [result for result in comparison_results if not is_known_term(result)]


def is_known_term(result: dict) -> bool:
    request = {"term": result.get("term"), "definition": result.get("definition", "")}
    return bool(find_existing_term(request))


def save_terms(comparison_results, company_name):
    save_new_terms(comparison_results, company_name)


def generate_and_save_embeddings(new_terms):
    for term_doc in new_terms:
        save_and_report_embedding(term_doc)


def save_and_report_embedding(term_doc: dict) -> None:
    term = term_doc.get("term")
    if not term:
        return

    embedding = embed_term(term_doc)
    save_term_embedding(term_doc, embedding)
    print(f"  Embedding opgeslagen voor: {term}")


def check_terms_in_vector_store(comparison_results):
    for result in comparison_results:
        report_term_status(result)


def report_term_status(result: dict) -> None:
    term = result.get("term")
    if not term:
        return

    request = {"term": term, "definition": result.get("definition", "")}
    existing_info = find_existing_term(request)
    if not existing_info:
        print(f"  + Nieuwe term: {term}")
        return

    print(f"  ✓ Bestaande kennis gevonden voor: {term}")


def generate_followup_prompts(request: dict, llm_client) -> tuple:
    technical_terms = extract_new_term_names(request["new_terms"])
    terms_text = format_terms_text(technical_terms)

    qa_request = {**request, "terms_text": terms_text, "technical_terms": technical_terms}
    prompts_response, answer_response = generate_followup_qa(qa_request, llm_client)

    rapport_request = {**request, "prompts_response": prompts_response, "answer_response": answer_response}
    rapport = generate_rapport(rapport_request, llm_client)

    return prompts_response, answer_response, rapport


def extract_new_term_names(new_terms: list) -> list:
    return [term for term in (result.get("term") for result in new_terms) if term]


def format_terms_text(technical_terms: list) -> str:
    return "\n".join(f"- {term}" for term in technical_terms)


def generate_followup_qa(request: dict, llm_client) -> tuple:
    technical_terms = request["technical_terms"]

    if not technical_terms:
        return "", "[]"

    filled_prompt = request["followup_prompts_prompt"].format(TECHNICAL_TERMS=request["terms_text"])
    prompts_response = llm_client.ask(filled_prompt)

    filled_answer_prompt = request["answer_followup_questions_prompt"].format(
        TECHNICAL_TERMS=request["terms_text"],
        FOLLOWUP_PROMPTS=prompts_response
    )
    answer_response = llm_client.ask(filled_answer_prompt)

    return prompts_response, answer_response


def generate_rapport(request: dict, llm_client) -> str:
    all_terms_text = format_all_terms_text(request["comparison_results"])

    filled_rapports_prompt = request["generate_rapports_prompt"].format(
        CUSTOMER_NAME=request["customer_name"],
        HUMINT_TEXT=request["humint_text"],
        TECHNICAL_TERMS=all_terms_text,
        FOLLOWUP_PROMPTS=request["prompts_response"],
        FOLLOWUP_ANSWERS=request["answer_response"]
    )
    return llm_client.ask(filled_rapports_prompt)


def format_all_terms_text(comparison_results: list) -> str:
    return "\n".join(
        f"- {result.get('term')}: {result.get('definition', '')}"
        for result in comparison_results
    )


def merge_followup_data(request: dict) -> list:
    clean_prompts = clean_json_block(request["followup_prompts"])
    clean_answers = clean_json_block(request["answer_response"])

    parsed_prompts = parse_json_safely(clean_prompts, "Followup prompts JSON incomplete, skipping.")
    parsed_answers = parse_json_safely(clean_answers, "Followup answers JSON incomplete, skipping.")

    lookups = {
        "definitions_by_term": build_definitions_by_term(request["comparison_results"]),
        "answers_by_term": build_answers_by_term(parsed_answers)
    }

    return merge_term_data(parsed_prompts, lookups)


def clean_json_block(text: str) -> str:
    return text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()


def parse_json_safely(text: str, error_message: str) -> list:
    if not text:
        return []

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print(error_message)
        return []


def build_definitions_by_term(comparison_results: list) -> dict:
    return {result["term"]: result.get("definition", "") for result in comparison_results}


def build_answers_by_term(parsed_answers: list) -> dict:
    return {item["term"]: extract_answers(item) for item in parsed_answers}


def extract_answers(item: dict) -> list:
    return [
        qa.get("answer", "") if isinstance(qa, dict) else qa
        for qa in item.get("followup_prompts", [])
    ]


def merge_term_data(parsed_prompts: list, lookups: dict) -> list:
    return [build_merged_term(item, lookups) for item in parsed_prompts]


def build_merged_term(item: dict, lookups: dict) -> dict:
    term = item["term"]
    return {
        "term": term,
        "definition": lookups["definitions_by_term"].get(term, ""),
        "followup_prompts": item.get("followup_prompts", []),
        "followup_answers": lookups["answers_by_term"].get(term, [])
    }
