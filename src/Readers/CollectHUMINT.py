import json
import os 

def collect_humint_data():

    choice = input(
        "Voor welk bedrijf wil je Human Intelligence vestrekken?"
        )

    humint=input(
        "Wil je tekst delen of een bestand uploaden? (tekst/bestand)?"
        )
    
    if humint.lower() == "bestand":
        file_path = input("Voer het pad naar het bestand in: ")
        if os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                humint = f.read()
        else:
            print("Bestand niet gevonden. Voer de informatie handmatig in.")
            humint = input("Voer de HUMINT-informatie in: ")
    if humint.lower() == "tekst":
        humint = input(
            "Voer de HUMINT-informatie in: "
        )

    infotype = input("Wat voor soort informatie is dit? (bijv. bedrijfsstrategie, productinformatie, marktinzichten): ")

    bron= input("Wat is de bron van deze informatie? (bijv. interne medewerker, externe consultant, openbare bron): ")

    reliability = input(
        "Hoe betrouwbaar acht je is deze bron? (1-10) "
        )

    reliability_check = input(
        "Waarom beschouw je deze informatie als betrouwbaar? "
    )

    return {
        "company": choice,
        "humint": humint,
        "reliability": reliability,
        "reason": reliability_check,
        "infotype": infotype,
        "bron": bron
    }


def save_humint_data(data):
    os.makedirs("src/output", exist_ok=True)
    
    output_path = f"data/humanInt/{data['company']}_humint.txt"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("HUMINT data saved successfully.")

