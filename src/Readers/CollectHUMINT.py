import json
import os


INTERVIEW_PROMPT = """Je bent een intelligence-analist die informatie verzamelt over {COMPANY} voor een intelligence-analyse.

Gesprek tot nu toe:
{CONVERSATION}

Jouw taak:
1. Lees het laatste antwoord van de gebruiker zorgvuldig
2. Als ze "geen idee" zeggen of iets niet weten, stel dan een eenvoudigere vraag of een andere invalshoek
3. Als ze iets nuttigs delen, vraag door op wat ze net zeiden
4. Leg kort uit waarom je de informatie verzamelt als dat helpt (bijv. "om een accuraat beeld te krijgen...")
5. Vraag ook naar de bron van de informatie als de gebruiker iets beweert — bijv. "Hoe weet je dat?" of "Waar heb je dat gelezen?"
6. Stel één natuurlijke, conversationele vervolgvraag

Als je minimaal 3 bruikbare antwoorden hebt verzameld inclusief minstens één bronvermelding, antwoord dan met exact: GENOEG_INFORMATIE

Stel alleen de vraag, geen inleiding."""

SUMMARY_PROMPT = """Je bent een intelligence-analist. Hieronder staat een gesprek over het technische landschap van {COMPANY}.

{CONVERSATION}

Vat dit gesprek samen als een gestructureerde HUMINT-tekst. Beschrijf welke technologieën, tools, platformen en systemen {COMPANY} gebruikt op basis van de verstrekte informatie. Schrijf in het Nederlands."""

FAKE_HUMINT_PROMPT = """Genereer een realistisch intern gesprek met een IT-manager van {COMPANY}.

Het gesprek is een interview in vraag-en-antwoord formaat tussen een analist en de IT-manager.
Het gaat over de technische infrastructuur van het bedrijf: welke tools, platformen, programmeertalen,
cloudomgevingen, databases, en systemen het bedrijf gebruikt.

Richtlijnen:
- Schrijf minimaal 10 uitgewisselde vragen en antwoorden
- Gebruik realistische en gedetailleerde technische informatie passend bij {COMPANY}
- Schrijf in het Nederlands
- Gebruik dit formaat:

**Analist:** [vraag]
**IT-manager:** [antwoord]

Begin het gesprek nu."""


def _run_interview(company, initial_input, llm_client):
    """Runs an LLM-guided interview based on initial input."""
    conversation = [f"Gebruiker: {initial_input}"]
    print()

    for _ in range(4):
        filled_prompt = INTERVIEW_PROMPT.format(
            COMPANY=company,
            CONVERSATION="\n".join(conversation)
        )
        question = llm_client.ask(filled_prompt).strip()

        if "GENOEG_INFORMATIE" in question:
            print("Genoeg informatie verzameld. Samenvatting wordt gemaakt...\n")
            break

        print(f"Vraag: {question}")
        answer = input("Jouw antwoord: ").strip()
        conversation.append(f"Analist: {question}")
        conversation.append(f"Gebruiker: {answer}")

    filled_summary = SUMMARY_PROMPT.format(
        COMPANY=company,
        CONVERSATION="\n".join(conversation)
    )
    summary = llm_client.ask(filled_summary)
    return summary


def collect_humint_data(llm_client=None):

    company = input("Voor welk bedrijf wil je Human Intelligence verstrekken? ").strip()

    while True:
        humint_choice = input(
            "Wil je tekst delen, een bestand uploaden, of HUMINT laten genereren? (tekst/bestand/genereer): "
        ).lower().strip()

        if humint_choice in ["tekst", "bestand", "genereer"]:
            break
        print("Ongeldige keuze. Probeer opnieuw (tekst/bestand/genereer).")

    if humint_choice == "bestand":
        file_path = input("Voer het pad naar het bestand in: ")
        if os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                initial_input = f.read()
        else:
            print("Bestand niet gevonden. Voer de informatie handmatig in.")
            initial_input = input("Wat weet je over dit bedrijf? ").strip()

        if llm_client:
            humint = _run_interview(company, initial_input, llm_client)
            infotype = "interview"
            bron = "gebruiker"
            reliability = "N/A"
            reliability_check = "Verzameld via LLM-gestuurd interview"
        else:
            humint = initial_input
            infotype, bron, reliability, reliability_check = _ask_metadata()

    elif humint_choice == "tekst":
        initial_input = input("Wat weet je over dit bedrijf? ").strip()

        if llm_client:
            humint = _run_interview(company, initial_input, llm_client)
            infotype = "interview"
            bron = "gebruiker"
            reliability = "N/A"
            reliability_check = "Verzameld via LLM-gestuurd interview"
        else:
            humint = initial_input
            infotype, bron, reliability, reliability_check = _ask_metadata()

    elif humint_choice == "genereer":
        if llm_client is None:
            print("Geen LLM-client beschikbaar. Voer de informatie handmatig in.")
            humint = input("Wat weet je over dit bedrijf? ").strip()
            infotype, bron, reliability, reliability_check = _ask_metadata()
        else:
            print(f"\nHUMINT wordt automatisch gegenereerd voor '{company}'...\n")
            filled_prompt = FAKE_HUMINT_PROMPT.format(COMPANY=company)
            humint = llm_client.ask(filled_prompt)
            print("HUMINT gegenereerd.\n")
            infotype = "automatisch gegenereerd"
            bron = "LLM-gegenereerd (demonstratie)"
            reliability = "N/A"
            reliability_check = "Automatisch gegenereerd door CIRQUI voor demonstratiedoeleinden."

    return {
        "company": company,
        "humint": humint,
        "reliability": reliability,
        "reason": reliability_check,
        "infotype": infotype,
        "bron": bron
    }


def _ask_metadata():
    infotype = input("Wat voor soort informatie is dit? (bijv. bedrijfsstrategie, productinformatie, marktinzichten): ")
    bron = input("Wat is de bron van deze informatie? (bijv. interne medewerker, externe consultant, openbare bron): ")
    reliability = input("Hoe betrouwbaar acht je deze bron? (1-10): ")
    reliability_check = input("Waarom beschouw je deze informatie als betrouwbaar? ")
    return infotype, bron, reliability, reliability_check


def save_humint_data(data):
    os.makedirs("data/humanInt", exist_ok=True)

    # Save full metadata as JSON
    json_path = f"data/humanInt/{data['company']}_humint.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    # Save just the text as .md for the pipeline
    md_path = f"data/humanInt/{data['company']}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(data["humint"])

    print(f"HUMINT data opgeslagen als {json_path} en {md_path}")