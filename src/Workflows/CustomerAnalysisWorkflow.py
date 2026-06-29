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
from Savers.JsonSaver import save_to_json, save_webint
from Savers.MarkdownSaver import save_to_markdown


def run_customer_analysis_workflow(customer_name: str = None, llm_client=None):
    if not customer_name:
        customer_name = input("Voer de naam van de klant in: ")

    if not llm_client:
        model = load_config()
        llm_client = LLMClient(model)

    print(f"\nCIRQUI start analyse voor: {customer_name}")
    print("─" * 40)

    technical_landscape_prompt, extract_terms_prompt, followup_prompts_prompt, answer_followup_questions_prompt, generate_rapports_prompt = load_prompts()

    print("📄 HUMINT wordt ingeladen...")
    humint_text = load_humint(customer_name)

    print("🌐 Technisch landschap wordt gegenereerd via Gemini...")
    technical_landscape_response = generate_technical_landscape(
        technical_landscape_prompt,
        customer_name,
        humint_text,
        llm_client
    )
    save_webint(customer_name, technical_landscape_response)
    print("✓ Technisch landschap opgeslagen.")

    print("\n🔍 Technische termen worden geëxtraheerd...")
    extracted_terms = extract_terms(
        technical_landscape_response,
        llm_client,
        extract_terms_prompt
    )
    print(f"✓ {len(extracted_terms)} termen gevonden.")

    print("\n🗄️  Termen worden vergeleken met database...")
    comparison_results = compare_terms_with_database(extracted_terms)

    check_terms_in_vector_store(comparison_results)

    new_terms_for_followup = [
        result for result in comparison_results
        if not find_existing_term(result.get("term"), result.get("definition", ""))
    ]
    print(f"✓ {len(new_terms_for_followup)} nieuwe termen gevonden.")

    print("\n💬 Vervolgvragen worden gegenereerd en beantwoord...")
    followup_prompts, answer_response, rapport = generate_followup_prompts(
        comparison_results,
        new_terms_for_followup,
        llm_client,
        followup_prompts_prompt,
        answer_followup_questions_prompt,
        generate_rapports_prompt,
        humint_text,
        customer_name
    )

    clean_prompts = followup_prompts.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    clean_answers = answer_response.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        parsed_prompts = json.loads(clean_prompts) if clean_prompts else []
    except json.JSONDecodeError:
        print("Followup prompts JSON incomplete, skipping.")
        parsed_prompts = []

    try:
        parsed_answers = json.loads(clean_answers) if clean_answers else []
    except json.JSONDecodeError:
        print("Followup answers JSON incomplete, skipping.")
        parsed_answers = []
 

    definitions_by_term = {result["term"]: result.get("definition", "") for result in comparison_results}
    answers_by_term = {
        item["term"]: [
            qa.get("answer", "") if isinstance(qa, dict) else qa
            for qa in item.get("followup_prompts", [])
        ]
        for item in parsed_answers
    }


    merged = []
    for item in parsed_prompts:
        term = item["term"]
        merged.append({
            "term": term,
            "definition": definitions_by_term.get(term, ""),
            "followup_prompts": item.get("followup_prompts", []),
            "followup_answers": answers_by_term.get(term, [])
        })

    print("\n📊 Analyse wordt opgeslagen...")
    save_to_json(customer_name, merged)
    print("✓ Analyse opgeslagen.")

    print("\n📝 Rapport wordt opgesteld...")
    save_to_markdown(customer_name, rapport)
    print("✓ Rapport opgeslagen.")

    print("\n💾 Nieuwe termen worden opgeslagen in database...")
    save_terms(comparison_results)

    print("\n🧠 Embeddings worden gegenereerd en opgeslagen...")
    generate_and_save_embeddings(new_terms_for_followup)

    print("\n" + "─" * 40)
    print(f"✅ Analyse voor {customer_name} voltooid!")


def load_config():
    config_reader = ConfigReader("data/config/config.txt")
    config_reader.read_config()
    return config_reader.get_config("model")


def load_prompts():
    prompt_templates = read_prompts("data/prompts")

    technical_landscape_prompt = prompt_templates[0]
    extract_terms_prompt = prompt_templates[1]
    generate_followup_prompts = prompt_templates[2]
    answer_followup_questions_prompt = prompt_templates[3]
    generate_rapports_prompt = prompt_templates[4]

    return (
        technical_landscape_prompt,
        extract_terms_prompt,
        generate_followup_prompts,
        answer_followup_questions_prompt,
        generate_rapports_prompt
    )


def load_humint(customer_name):
    humint_reader = HumintReader(f"data/humanInt/{customer_name}.md")
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
    existing_terms = load_existing_terms()
    return compare_terms(extracted_terms, existing_terms)


def save_terms(comparison_results):
    save_new_terms(comparison_results)


def generate_and_save_embeddings(new_terms):
    for term_doc in new_terms:
        term = term_doc.get("term")
        if not term:
            continue
        embedding = embed_term(term_doc)
        save_term_embedding(term_doc, embedding)
        print(f"  Embedding opgeslagen voor: {term}")


def check_terms_in_vector_store(comparison_results):
    for result in comparison_results:
        term = result.get("term")
        if not term:
            continue
        existing_info = find_existing_term(term, result.get("definition", ""))
        if existing_info:
            print(f"  ✓ Bestaande kennis gevonden voor: {term}")
        else:
            print(f"  + Nieuwe term: {term}")


def generate_followup_prompts(
    comparison_results,
    new_terms,
    llm_client,
    followup_prompts_prompt,
    answer_followup_questions_prompt,
    generate_rapports_prompt,
    humint_text,
    customer_name
):
    technical_terms = []

    for result in new_terms:
        term = result.get("term")
        if term:
            technical_terms.append(term)

    terms_text = "\n".join(f"- {term}" for term in technical_terms)

    if technical_terms:
        filled_prompt = followup_prompts_prompt.format(
            TECHNICAL_TERMS=terms_text
        )
        prompts_response = llm_client.ask(filled_prompt)

        filled_answer_prompt = answer_followup_questions_prompt.format(
            TECHNICAL_TERMS=terms_text,
            FOLLOWUP_PROMPTS=prompts_response
        )
        answer_response = llm_client.ask(filled_answer_prompt)
    else:
        prompts_response = ""
        answer_response = "[]"

    all_terms_text = "\n".join(
        f"- {result.get('term')}: {result.get('definition', '')}"
        for result in comparison_results
    )

    filled_rapports_prompt = generate_rapports_prompt.format(
        CUSTOMER_NAME=customer_name,
        HUMINT_TEXT=humint_text,
        TECHNICAL_TERMS=all_terms_text,
        FOLLOWUP_PROMPTS=prompts_response,
        FOLLOWUP_ANSWERS=answer_response
    )
    rapport = llm_client.ask(filled_rapports_prompt)

    return prompts_response, answer_response, rapport