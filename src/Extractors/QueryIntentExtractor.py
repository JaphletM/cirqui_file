from Services.LLMclient import LLMClient

ALLOWED_INTENTS = {"bedrijven", "definitie"}

def validate_intent(raw: dict) -> dict:
    intent= raw.get("intent") 
    if intent not in ALLOWED_INTENTS:
        raise ValueError(f"Invalid intent: {intent}. Allowed intents are: {ALLOWED_INTENTS}")
    
    terms=raw.get("terms")
    if not isinstance(terms, list):
        raise ValueError(f"Invalid terms: {terms}. Terms must be a list.") 
    return {"intent": intent, "terms": terms}


def extract_query_intent(question: str, llm_client: LLMClient, prompt_template: str) -> dict:
    
    raise NotImplementedError
