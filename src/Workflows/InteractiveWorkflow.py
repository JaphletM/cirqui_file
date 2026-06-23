from Readers.CollectHUMINT import collect_humint_data, save_humint_data
from Workflows.CustomerAnalysisWorkflow import run_customer_analysis_workflow
def interactive_workflow():
    while True:
        menu = input(
            "\nA) Analyse klant\n"
            "B) Verzamel HUMINT\n"
            "C) Exit\n"
        )

        if menu.upper() == "A":
            run_customer_analysis_workflow()

        elif menu.upper() == "B":
            humint_data = collect_humint_data()
            save_humint_data(humint_data)

        elif menu.upper() == "C":
            break