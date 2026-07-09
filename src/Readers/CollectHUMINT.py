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


def collect_humint_data(llm_client=None):
    company = input("Voor welk bedrijf wil je Human Intelligence verstrekken? ").strip()
    humint_choice = ask_humint_choice()

    request = {"company": company, "llm_client": llm_client}
    humint, metadata = collect_humint_for_choice(humint_choice, request)

    return {
        "company": company,
        "humint": humint,
        "reliability": metadata["reliability"],
        "reason": metadata["reliability_check"],
        "infotype": metadata["infotype"],
        "bron": metadata["bron"]
    }


def ask_humint_choice():
    while True:
        choice = input(
            "Wil je tekst delen, een bestand uploaden, of HUMINT laten genereren? (tekst/bestand/genereer): "
        ).lower().strip()

        if choice in ["tekst", "bestand", "genereer"]:
            return choice

        print("Ongeldige keuze. Probeer opnieuw (tekst/bestand/genereer).")


def collect_humint_for_choice(choice, request):
    if choice == "bestand":
        return collect_from_file(request)

    if choice == "tekst":
        return collect_from_text(request)

    return collect_generated(request)


def collect_from_file(request):
    file_path = input("Voer het pad naar het bestand in: ")
    initial_input = read_file_or_ask(file_path)

    return collect_with_optional_interview(request, initial_input)


def read_file_or_ask(file_path):
    if os.path.isfile(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    print("Bestand niet gevonden. Voer de informatie handmatig in.")
    return input("Wat weet je over dit bedrijf? ").strip()


def collect_from_text(request):
    initial_input = input("Wat weet je over dit bedrijf? ").strip()
    return collect_with_optional_interview(request, initial_input)


def collect_with_optional_interview(request, initial_input):
    llm_client = request["llm_client"]

    if not llm_client:
        return initial_input, ask_metadata()

    interview_request = {**request, "initial_input": initial_input}
    humint = run_interview(interview_request)
    metadata = {
        "infotype": "interview",
        "bron": "gebruiker",
        "reliability": "N/A",
        "reliability_check": "Verzameld via LLM-gestuurd interview"
    }
    return humint, metadata


def collect_generated(request):
    llm_client = request["llm_client"]

    if not llm_client:
        print("Geen LLM-client beschikbaar. Voer de informatie handmatig in.")
        humint = input("Wat weet je over dit bedrijf? ").strip()
        return humint, ask_metadata()

    print(f"\nHUMINT wordt automatisch gegenereerd voor '{request['company']}'...\n")
    filled_prompt = FAKE_HUMINT_PROMPT.format(COMPANY=request["company"])
    humint = llm_client.ask(filled_prompt)
    print("HUMINT gegenereerd.\n")

    metadata = {
        "infotype": "automatisch gegenereerd",
        "bron": "LLM-gegenereerd (demonstratie)",
        "reliability": "N/A",
        "reliability_check": "Automatisch gegenereerd door CIRQUI voor demonstratiedoeleinden."
    }
    return humint, metadata


def run_interview(request):
    llm_client = request["llm_client"]
    conversation = [f"Gebruiker: {request['initial_input']}"]
    print()

    round_request = {"company": request["company"], "conversation": conversation}
    for _ in range(4):
        answered_enough = conduct_interview_round(round_request, llm_client)
        if answered_enough:
            break

    filled_summary = SUMMARY_PROMPT.format(
        COMPANY=request["company"],
        CONVERSATION="\n".join(conversation)
    )
    return llm_client.ask(filled_summary)


def conduct_interview_round(round_request, llm_client):
    company = round_request["company"]
    conversation = round_request["conversation"]

    filled_prompt = INTERVIEW_PROMPT.format(COMPANY=company, CONVERSATION="\n".join(conversation))
    question = llm_client.ask(filled_prompt).strip()

    if "GENOEG_INFORMATIE" in question:
        print("Genoeg informatie verzameld. Samenvatting wordt gemaakt...\n")
        return True

    print(f"Vraag: {question}")
    answer = input("Jouw antwoord: ").strip()
    conversation.append(f"Analist: {question}")
    conversation.append(f"Gebruiker: {answer}")
    return False


def ask_metadata():
    return {
        "infotype": input("Wat voor soort informatie is dit? (bijv. bedrijfsstrategie, productinformatie, marktinzichten): "),
        "bron": input("Wat is de bron van deze informatie? (bijv. interne medewerker, externe consultant, openbare bron): "),
        "reliability": input("Hoe betrouwbaar acht je deze bron? (1-10): "),
        "reliability_check": input("Waarom beschouw je deze informatie als betrouwbaar? ")
    }


def save_humint_data(data):
    os.makedirs("data/humanInt", exist_ok=True)

    json_path = f"data/humanInt/{data['company']}_humint.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    md_path = f"data/humanInt/{data['company']}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(data["humint"])

    print(f"HUMINT data opgeslagen als {json_path} en {md_path}")
