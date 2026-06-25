import json

def extract_technical_terms(text, llm_client, prompt_template):
    prompt = prompt_template.format(TEXT=text)
    response = llm_client.ask(prompt)

    try:
        clean = response.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(clean)
    
    except json.JSONDecodeError:
        print("Invalid JSON returned by LLM:")
        print(response)
        return []