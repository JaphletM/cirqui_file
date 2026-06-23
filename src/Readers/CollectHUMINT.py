import json
import os 

def collect_humint_data():

    choice = input(
        "Voor welk bedrijf wil je Human Intelligence vestrekken?"
        )

    humint=input(
        "Wil je tekst delen of een bestand uploaden? (tekst/bestand)?"
        )

    reliability = input(
        "Hoe betrouwbaar acht je is deze informatie? (1-10) "
        )

    reliability_check = input(
        "Waarom beschouw je deze informatie als betrouwbaar? "
    )

    return {
        "company": choice,
        "humint": humint,
        "reliability": reliability,
        "reason": reliability_check
    }


def save_humint_data(data):
    os.makedirs("src/output", exist_ok=True)
    
    output_path = f"data/humanInt/{data['company']}_humint.txt"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("HUMINT data saved successfully.")


humint_data = collect_humint_data()
save_humint_data(humint_data)