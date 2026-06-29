from Readers.CollectHUMINT import collect_humint_data, save_humint_data
from Workflows.CustomerAnalysisWorkflow import run_customer_analysis_workflow
from Services.LLMclient import LLMClient
from Readers.ConfigReader import ConfigReader


def interactive_workflow():
    config = ConfigReader("data/config/config.txt")
    config.read_config()
    model = config.get_config("model")
    llm_client = LLMClient(model)

    print("Welkom bij CIRQUI! Dit is een interactieve workflow voor het analyseren van bedrijven en het verzamelen van Human Intelligence.")
    print("Kies een optie uit het menu:")

    while True:
        menu = input(
            "\nA) Genereer een rapport over het technische landschap van een bedrijf\n"
            "B) Verzamel Human Intelligence over een bedrijf en genereer een rapport\n"
            "C) Exit\n"
        ).upper().strip()

        if menu == "A":
            run_customer_analysis_workflow(llm_client=llm_client)
            print("\nRapport is gegenereerd en opgeslagen.")
            print("Wat wil je nu doen?")

        elif menu == "B":
            humint_data = collect_humint_data(llm_client=llm_client)
            save_humint_data(humint_data)
            print(f"\nHUMINT opgeslagen. Rapport wordt gegenereerd voor {humint_data['company']}...\n")
            run_customer_analysis_workflow(customer_name=humint_data["company"], llm_client=llm_client)
            print(f"\nRapport voor {humint_data['company']} is gegenereerd en opgeslagen.")
            print("Wat wil je nu doen?")

        elif menu == "C":
            print("\nTot ziens!")
            break

        else:
            print("Ongeldige keuze. Kies A, B of C.")