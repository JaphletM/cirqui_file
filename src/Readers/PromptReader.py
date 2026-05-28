from pathlib import Path


def read_prompts(prompt_directory):
    prompts = []

    prompt_directory = Path(prompt_directory)

    for file_path in sorted(
        prompt_directory.glob("*.md")
    ):
        content = file_path.read_text(
            encoding="utf-8"
        )

        prompts.append(content)

    return prompts