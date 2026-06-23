from Readers.CollectHUMINT import collect_humint_data, save_humint_data
from Workflows.CustomerAnalysisWorkflow import run_customer_analysis_workflow
def interactive_workflow():
    print("Welkom bij CIRQUI! Dit is een interactieve workflow voor het analyseren van bedrijven en het verzamelen van Human Intelligence.") 
    print("Kies een optie uit het menu:")
    while True: 
        menu = input(
            "\nA) Genereer een rapport over de technische landscape van een bedrijf\n"
            "B) Verzamel Human Intelligence over een bedrijf\n"
            "C) Exit\n"
        )

        if menu.upper() == "A":
            run_customer_analysis_workflow()

        elif menu.upper() == "B":
            humint_data = collect_humint_data()
            save_humint_data(humint_data)

        elif menu.upper() == "C":
            break