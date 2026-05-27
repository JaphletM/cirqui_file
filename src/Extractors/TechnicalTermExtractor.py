import json


class TechnicalTermExtractor:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def extract(self, text):
        prompt = f"""
Extract technical terms from the following text.

Return ONLY valid JSON.
Do not include explanations.
Do not include markdown.
Do not wrap the JSON in ```.

Use this exact format:

[
    {{
        "term": "Docker",
        "definition": "A platform for building and running containerized applications.",
        "category": "DevOps"
    }}
]

Text:
{text}
"""

        response = self.llm_client.ask(prompt)

        try:
            return json.loads(response)

        except json.JSONDecodeError:
            print("Invalid JSON returned by LLM:")
            print(response)

            return []