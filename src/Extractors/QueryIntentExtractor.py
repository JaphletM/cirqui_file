import json

from Services.LLMclient import LLMClient

ALLOWED_INTENTS = {"bedrijven", "definitie", "technologieen"}

def validate_intent(raw: dict) -> dict:
    intent= raw.get("intent") 
    if intent not in ALLOWED_INTENTS:
        raise ValueError(f"Invalid intent: {intent}. Allowed intents are: {ALLOWED_INTENTS}")
    
    terms=raw.get("terms")
    if not isinstance(terms, list):
        raise ValueError(f"Invalid terms: {terms}. Terms must be a list.") 
    if not terms:
        raise ValueError("Terms list cannot be empty.")
    if any(not isinstance(term, str) or not term.strip() for term in terms):
        raise ValueError(f"Invalid term in terms list: {terms}. Each term must be a non-empty string.")
    return {"intent": intent, "terms": terms}
                    


def extract_query_intent(question: str, llm_client: LLMClient, prompt_template: str) -> dict:
    filled_prompt = prompt_template.replace("{QUESTION}", question)
    response = llm_client.ask(filled_prompt)

    clean_response = response.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    start = clean_response.find("{")
    end = clean_response.rfind("}")
    if start != -1 and end != -1:
        clean_response = clean_response[start:end + 1]

    try:
        raw = json.loads(clean_response)
    except json.JSONDecodeError:
        raise ValueError(f"kon LLM-antwoord niet als JSON parsen: {response!r}")

    return validate_intent(raw)
