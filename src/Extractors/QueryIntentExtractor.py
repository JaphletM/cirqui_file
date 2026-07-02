from Services.LLMclient import LLMClient

ALLOWED_INTENTS = {"bedrijven", "definitie"}

def validate_intent(raw: dict) -> dict:
    raise NotImplementedError


def extract_query_intent(question: str, llm_client: LLMClient, prompt_template: str) -> dict:
    raise NotImplementedError
