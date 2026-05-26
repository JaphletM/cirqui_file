from Readers.PromptReader import PromptReader
from Readers.ConfigReader import ConfigReader
from Readers.HUMIntReader import HumintReader
from LLMclient import LLMClient


#prompt-lader
config_reader = ConfigReader("data/config/config.txt")
config_reader.read_config()

customer_name = config_reader.get_config("customer_name")

model = config_reader.get_config(
    "model"
)

reader = PromptReader("data/prompts/001-technical-landscape.md")

template = reader.read_prompt()


humint_reader = HumintReader(
    f"data/humanInt/{customer_name}.md"
)

humint_text = humint_reader.read_humint()

print(humint_text)

filled_prompt = template.format(
    CUSTOMER_NAME=customer_name
)

print(filled_prompt)

llm_client = LLMClient(model)

response = llm_client.ask(filled_prompt)
print(response)



