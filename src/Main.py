from Readers.PromptReader import PromptReader
from Readers.ConfigReader import ConfigReader
from Readers.HUMIntReader import HumintReader


#prompt-lader
config_reader = ConfigReader("data/config/config.txt")
config_reader.read_config()

customer_name = config_reader.get_config("customer_name")

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
