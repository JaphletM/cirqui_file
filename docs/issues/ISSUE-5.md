# ISSUE-5: Chatbot CLI end-to-end voor Jeroen

## User story

Als Jeroen wil ik CIRQUI kunnen opstarten, een vraag typen, en direct een
antwoord zien — net zoals de bestaande menu-opties voor rapportages —
zodat ik zonder technische kennis bij de verzamelde informatie kan.

## Depends on

ISSUE-1, ISSUE-2, ISSUE-3, ISSUE-4 (dit issue verbindt alle voorgaande
stappen en ontsluit ze via de CLI).

## Business rules covered

Alle regels uit ISSUE-1 t/m ISSUE-4, plus: technische validatiefouten
(bijv. een onherkenbare vraag) worden op de delivery-grens vertaald naar
een begrijpelijke Nederlandse boodschap — Jeroen krijgt nooit een
stacktrace of Engelse foutmelding te zien.

## Proposed file tree

```
src/Workflows/
  ChatbotWorkflow.py                 # AFRONDEN — run_chatbot_query toevoegen
  InteractiveWorkflow.py             # UITBREIDEN — nieuwe menu-optie

src/Readers/
  Chatbot.py                         # INVULLEN — bestaat al als lege stub

tests/Workflows/
  test_chatbot_workflow.py           # UITBREIDEN — end-to-end pipeline tests
tests/Readers/
  test_chatbot_cli.py                # NIEUW
```

## Functions

### `run_chatbot_query(question: str, llm_client) -> str` — `src/Workflows/ChatbotWorkflow.py`

- **Verantwoordelijkheid:** de volledige pipeline uitvoeren voor één
  vraag: `extract_query_intent` → `resolve_query_terms` →
  `gather_query_results` → `compose_answer`.
- **Input:** `question: str`, `llm_client`.
- **Output:** `str` — het definitieve Nederlandse antwoord.
- **Failures:**
  - `QueryIntentParseError` of `InvalidQueryIntentError` (uit ISSUE-1)
    worden hier opgevangen en omgezet naar een vast Nederlands bericht,
    bijv. `"Ik kon je vraag niet goed interpreteren. Kun je het anders
    formuleren?"` — dit is de grens waar technische fouten
    gebruikersfeedback worden.
  - overige infrastructuurfouten (Qdrant/Mongo onbereikbaar) propageren
    bewust **niet** stilzwijgend als een leeg antwoord; ze worden
    doorgegeven aan de delivery-laag, die ze op zijn beurt netjes toont
    (zie `run_chatbot`).
- **Dependencies:** alle functies uit ISSUE-1 t/m ISSUE-4.
- **Business rule of I/O:** orkestratie; dit is de enige publieke
  ingang van de chatbot-pipeline.

### `run_chatbot(llm_client=None) -> None` — `src/Readers/Chatbot.py`

- **Verantwoordelijkheid:** CLI-lus, in dezelfde stijl als
  `collect_humint_data` in `Readers/CollectHUMINT.py`: vraagt Jeroen om
  input, roept `run_chatbot_query` aan, print het antwoord, herhaalt tot
  een stopcommando (`"stop"` / `"exit"`).
- **Input:** optionele `llm_client` (als `None`, zelf opbouwen via
  `ConfigReader` + `LLMClient`, analoog aan `run_customer_analysis_workflow`).
- **Output:** geen (side-effecting: `print`).
- **Failures:** infrastructuurfouten die uit `run_chatbot_query`
  omhoogkomen worden hier gevangen en getoond als
  `"Er ging iets mis bij het ophalen van de informatie. Probeer het
  opnieuw."` — de gebruiker ziet nooit een ruwe exceptie.
- **Dependencies:** `run_chatbot_query`, `ConfigReader`, `LLMClient`.
- **Business rule of I/O:** delivery (CLI I/O).

### Wijziging in `src/Workflows/InteractiveWorkflow.py`

- Nieuwe menu-optie toevoegen (bijv. `D`) die `run_chatbot(llm_client)`
  aanroept, naast de bestaande opties A/B/C. Puur bekabeling, geen nieuwe
  logica.

## Required tests

- `run_chatbot_query`, met gemockte `extract_query_intent`,
  `resolve_query_terms`, `gather_query_results`, `compose_answer`:
  - happy path `bedrijven` (Type 1 uit `docs/chatbot-userstory.md`):
    Kubernetes → `["Google", "ASML"]`
  - happy path `definitie` (Type 2): Kubernetes → definitietekst
  - happy path `samengesteld` (Type 3): Kubernetes ∩ Java ∩ Linux →
    `["Google"]` (exact het voorbeeld uit de userstory)
  - geen bevestigde match → deterministisch "geen resultaten"-antwoord
    (uit ISSUE-4), geen LLM-call voor de formulering
  - ongeldige/onparsebare intent van het LLM → het vaste Nederlandse
    "kon je vraag niet interpreteren"-bericht, geen crash
- `run_chatbot` (CLI): `builtins.input` gemockt met één vraag gevolgd
  door `"stop"`; assert dat `run_chatbot_query` is aangeroepen met de
  juiste vraag en dat de output op stdout het teruggegeven antwoord bevat
- `run_chatbot`: gemockte infrastructuurfout uit `run_chatbot_query` →
  toont de nette foutmelding, crasht niet, lus stopt of gaat door volgens
  ontwerpkeuze (vastleggen in de test welke van de twee)

## Openstaande vragen (niet in scope van dit issue, wel relevant voor vervolg)

Overgenomen uit `docs/chatbot-userstory.md`, nog onbeantwoord:

- Multi-turn gesprekken (vervolgvragen die verwijzen naar een vorig
  antwoord) — nu niet ondersteund, elke vraag is stateless.
- Hoeveel resultaten er maximaal getoond worden bij een groot aantal
  gevonden bedrijven/termen.
- Of bronvermelding (en eventueel een echte URL i.p.v. een beschrijving)
  in het antwoord moet komen.
