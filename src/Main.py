from Extractors.TermComparator import compare_terms
from Readers.PromptReader import PromptReader
from Readers.ConfigReader import ConfigReader
from Readers.HUMIntReader import HumintReader
from LLMclient import LLMClient
from Extractors.TechnicalTermExtractor import TechnicalTermExtractor
from database import load_existing_terms, save_new_terms


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
#print(response)

technical_term_extractor = TechnicalTermExtractor(llm_client)

extracted_terms= technical_term_extractor.extract(response) 

print(extracted_terms)


existing_terms = load_existing_terms()

comparison_results = compare_terms(
    extracted_terms,
    existing_terms
)

for result in comparison_results:
    print(result)

save_new_terms(comparison_results)

