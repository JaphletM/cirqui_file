import json


def extract_technical_terms(text, llm_client, prompt_template):
    prompt = prompt_template.format(
        TEXT=text
    )

    response = llm_client.ask(prompt)

    try:
        return json.loads(response)

    except json.JSONDecodeError:
        print("Invalid JSON returned by LLM:")
        print(response)
        return [] 