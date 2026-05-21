# prompt_reader.py
from pathlib import Path


class PromptReader:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def read_prompts(self) -> list[str]:
        if not self.file_path.exists():
            raise FileNotFoundError(
                f"Prompt file not found: {self.file_path}"
            )

        content = self.file_path.read_text(encoding="utf-8")

        prompts = [
            prompt.strip()
            for prompt in content.split("---")
            if prompt.strip()
        ]

        return prompts