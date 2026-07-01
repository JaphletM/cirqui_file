## Chatbot User Story 
User: Jeroen (CEO) — niet-technisch, wil zonder SQL of database kennis vragen kunnen stellen over het technische landschap van klanten.

## Goals
Natuurlijke taalvragen stellen over welke bedrijven welke technische tools gebruiken en een leesbaar antwoord terugkrijgen.
Ondersteunde vraagtypes:
Type 1 — Bedrijven opzoeken: "Welke bedrijven gebruiken Kubernetes?" → zoekt term → geeft lijst van bedrijven terug
Type 2 — Term opzoeken: "Wat is Kubernetes?" → zoekt term → geeft definitie terug


Binnen scope: Technische termen die al in de database staan, enkelvoudige vragen


Buiten scope voor nu: CV lezen, CV-matching, data toevoegen of aanpassen


## Acceptance criteria
- Zoeken is hoofdletter-ongevoelig (case insensitive)
- Gedeeltelijke zoekopdrachten geven relevante resultaten terug
- Spelfouten worden tolerant behandeld door semantisch zoeken
- Bij geen resultaten krijgt de gebruiker een duidelijke melding
- Resultaten bevatten de bedrijfsnaam én context over waarom ze matchen
- Antwoord matcht de input (engels of nederlands)


Open vragen:

-Wil je multi-turn gesprekken? Bijvoorbeeld "welke bedrijven gebruiken Kubernetes?" gevolgd door "wat gebruikt Google nog meer?" 

-Hoeveel resultaten teruggeven per vraag?


-Moet het systeem samengestelde zoekopdrachten ondersteunen? 
    Bijvoorbeeld: "Welke bedrijven gebruiken Kubernetes. Linux én Java? (intersectie?)

- Bronnen zijn opgeslagen als beschrijvingen, niet als URLs 
  (bv. "Engineering blog" in plaats van "https://..."). 
  Moeten we de pipeline aanpassen om ook de daadwerkelijke URL 
  op te slaan zodat de chatbot naar de bron kan linken?

- Moeten chatbot antwoorden de bron vermelden zodat Jeroen kan 
  zien hoe betrouwbaar de informatie is? 
  (bv. "APG gebruikt Java — bron: officiële bedrijfswebsite")


## Process

Type 1 — Bedrijven opzoeken:
Jeroen: "Welke bedrijven gebruiken Kubernetes?"
=>
LLM analyseert vraag → intent: "bedrijven", term: "Kubernetes"
=>
Embed "Kubernetes"
=>
Zoek in Qdrant → vindt "Kubernetes" term
=>
Zoek in MongoDB → geeft companies array: [Google, ASML]
=>
LLM formatteert: "Google en ASML gebruiken Kubernetes voor..."

Type 2 — Term opzoeken:
Jeroen: "Wat is Kubernetes?"
=>
LLM analyseert vraag → intent: "definitie", term: "Kubernetes"
=>
Embed "Kubernetes"
=>
Zoek in Qdrant → vindt term + definitie in payload
=>
LLM formatteert: "Kubernetes is een systeem voor..."

Type 3 — Samengestelde zoekopdracht:
Jeroen: "Welke bedrijven gebruiken Kubernetes, Java en Linux?"
=>
LLM analyseert vraag → intent: "samengesteld", termen: ["Kubernetes", "Java", "Linux"]
=>
Embed en zoek elke term apart in Qdrant
=>
Zoek per term in MongoDB → companies per term
Kubernetes: [Google, ASML]
Java: [Google, Booking]
Linux: [Google, ASML, Booking]
=>
Intersectie: alleen bedrijven die in ALLE lijsten voorkomen → [Google]
=>
LLM formatteert: "Google gebruikt alle drie: Kubernetes, Java en Linux"


## Nog te implementeren
- Volledige rapporten opslaan in Qdrant als vectoren (staat in de opdracht, 
  nog niet gebouwd)
