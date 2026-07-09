import json

def extract_technical_terms(request, llm_client):
    prompt = request["prompt_template"].format(TEXT=request["text"])
    response = llm_client.ask(prompt)

    try:
        clean = response.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(clean)
    
    except json.JSONDecodeError:
        print("Invalid JSON returned by LLM:")
        print(response)
        return []