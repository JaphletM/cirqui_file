##llm-client
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    def __init__(self, model: str):
        self.model = model

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )

    def ask(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content