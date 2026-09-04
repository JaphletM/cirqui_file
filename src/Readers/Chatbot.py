from Readers.ConfigReader import ConfigReader
from Services.LLMclient import LLMClient
from Workflows.ChatbotWorkflow import run_chatbot_query


def run_chatbot(llm_client=None) -> None:
    if llm_client is None:
        config_reader = ConfigReader("data/config/config.txt")
        config_reader.read_config()
        model = config_reader.get_config("model")
        llm_client = LLMClient(model)

    with open("data/prompts/006-query-intent.md", encoding="utf-8") as f:
        prompt_template_intent = f.read()

    with open("data/prompts/007-answer-formatter.md", encoding="utf-8") as f:
        prompt_template_answer = f.read()

    prompt_templates = {"intent": prompt_template_intent, "answer": prompt_template_answer}

    print("Welkom bij de chatbot! Typ 'exit' om te stoppen.")
    while True:
        question = input("Stel een vraag in de vorm 'Wat is de \"technische term\"' of 'Welke bedrijven werken met  \"technische term\"': ")
        if question.lower() == "exit":
            break

        request = {"question": question, "prompt_templates": prompt_templates}

        try:
            answer = run_chatbot_query(request, llm_client)
            print(f"Antwoord: {answer}")
        except Exception as e:
            print(f"Er is een fout opgetreden: {e}")

    return None
