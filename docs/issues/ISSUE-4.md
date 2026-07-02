# ISSUE-4: Antwoord samenstellen in natuurlijke taal (Nederlands)

## User story

**Epic:** Als CEO wil ik vragen kunnen stellen over het technische
landschap van een klant, zodat ik hen vaardige mensen kan aanbieden.

Dit issue behandelt daarvan de presentatie: ik wil een leesbaar antwoord
in het Nederlands krijgen op mijn vraag, en een duidelijke melding als er
niets gevonden is, zodat ik nooit zelf ruwe data hoef te interpreteren.

## Depends on

ISSUE-3 (levert een `QueryResult`).

## Business rules covered

- Antwoorden zijn altijd in het Nederlands.
- Bij geen resultaten krijgt de User een duidelijke melding.
- De chatbot informeert alleen — geen aanbevelingen of beslissingen in
  het antwoord.

## Let op — afwijking t.o.v. `docs/chatbot-userstory.md`

Dat document noemt als acceptatiecriterium "antwoord matcht de input
(engels of nederlands)", terwijl de opdracht voor dit issue expliciet
stelt: **antwoorden altijd in het Nederlands**. Dit issue implementeert
de expliciete opdracht-eis (altijd Nederlands). Als meertaligheid alsnog
gewenst is, is dat een aparte, bewuste scope-uitbreiding — niet iets om
stilzwijgend open te laten.

## Proposed file tree

```
data/prompts/
  007-answer-formatter.md            # NIEUW

src/Extractors/
  AnswerComposer.py                  # NIEUW

tests/Extractors/
  test_answer_composer.py            # NIEUW
```

## Functions

### `QueryResult` (dataclass, domain) — `src/Extractors/AnswerComposer.py`

- **Velden:** `intent: str`, `terms: list[str]`, `found: bool`,
  `companies_per_term: dict[str, list[str]] | None`,
  `companies_intersection: list[str] | None` (alleen gevuld bij `bedrijven`
  met 2+ termen — zie ISSUE-3), `definitions: dict[str, str] | None`.
- **Business rule of I/O:** business rule — het feit dat dit object géén
  velden heeft voor aanbevelingen/acties is de structurele afdwinging
  van "de chatbot informeert alleen".

### `build_answer_context(result: QueryResult) -> dict` — `src/Extractors/AnswerComposer.py`

- **Verantwoordelijkheid:** `QueryResult` omzetten naar de exacte data die
  in het antwoord-prompt gaat — puur feiten, geen state buiten wat is
  meegegeven. Bij meerdere termen krijgt het LLM zowel de lijst per term
  als de intersectie aangereikt, en beslist zelf welke framing het beste
  bij de gestelde vraag past (zie ISSUE-1: dat is bewust niet al bij de
  intent-classificatie vastgelegd).
- **Input:** `QueryResult`. **Output:** `dict`, bijv.
  ```
  {
    "gevonden": bool,
    "termen": [...],
    "bedrijven_per_term": {...} | None,
    "bedrijven_intersectie": [...] | None,
    "definities": {...} | None
  }
  ```
- **Failures:** geen (pure transformatie).
- **Dependencies:** geen.
- **Business rule of I/O:** business rule, pure en testbaar zonder LLM.

### `compose_answer(result: QueryResult, llm_client, prompt_template: str) -> str` — `src/Extractors/AnswerComposer.py`

- **Verantwoordelijkheid:** het uiteindelijke Nederlandstalige antwoord
  produceren. Volgt het bestaande "vul prompt-template → `llm_client.ask`"
  patroon dat al meermaals voorkomt in `CustomerAnalysisWorkflow.py`
  (`generate_technical_landscape`, `generate_followup_prompts`) — geen
  nieuwe generieke "prompt-runner"-functie nodig, dit blijft één
  functie-aanroep, dus er is niets om te extraheren of te dupliceren.
- **Beslissing (business rule, geen LLM-afhankelijkheid voor de
  belangrijkste garantie):** als `result.found is False`, wordt **geen**
  LLM-call gedaan. Er wordt een vast, deterministisch Nederlands bericht
  teruggegeven, bijv.:
  `f"Geen informatie gevonden over: {', '.join(result.terms)}."`
  Dit garandeert de "duidelijke melding bij geen resultaten"-regel zonder
  te vertrouwen op het LLM om dat elke keer correct te verwoorden, en
  maakt de regel unit-testbaar zonder een LLM te mocken op tekstniveau.
- **Input:** `QueryResult`, `llm_client`, `prompt_template` (alleen
  gebruikt als `result.found is True`).
- **Output:** `str`.
- **Failures:** geen expliciete nieuwe foutklasse nodig; LLM-fouten
  propageren zoals elders in de codebase (`llm_client.ask`).
- **Dependencies:** `build_answer_context`, `llm_client.ask`.
- **Business rule of I/O:** mix — de no-results-tak is een pure business
  rule, de found-tak is een I/O-boundary (LLM-aanroep). Dit is bewust:
  de kritieke garantie (duidelijke melding) mag niet van het LLM afhangen.

## Prompt: `data/prompts/007-answer-formatter.md`

Moet expliciet instrueren:
- Antwoord **altijd in het Nederlands**, ongeacht de taal van de vraag.
- Gebruik **uitsluitend** de meegegeven feiten (`gevonden`, `termen`,
  `bedrijven_per_term`, `bedrijven_intersectie`, `definities`) — geen
  aannames, geen aanbevelingen, geen vervolgacties voorstellen namens
  de User.
- Bij meerdere termen: als `bedrijven_intersectie` niet leeg is, benoem
  die duidelijk ("X gebruikt alle genoemde technologieën"); benoem
  daarnaast ook kort de losse resultaten per term uit
  `bedrijven_per_term`, inclusief termen waarvoor niets is gevonden — dat
  mag niet stilzwijgend verdwijnen uit het antwoord.

## Required tests

- `build_answer_context` voor `found=True`, intent `bedrijven`, 1 term →
  dict bevat `bedrijven_per_term`, `bedrijven_intersectie is None`, geen
  `definities`, geen "aanbeveling"-achtige key
- `build_answer_context` voor `found=True`, intent `bedrijven`, 3 termen
  (Kubernetes/Java/Linux-voorbeeld) → dict bevat zowel
  `bedrijven_per_term` (drie losse lijsten) als
  `bedrijven_intersectie == ["Google"]`
- `build_answer_context` voor `found=False` → dict signaleert duidelijk
  "niet gevonden" (bijv. `gevonden: False`)
- `compose_answer` met `result.found=False` → retourneert het vaste
  Nederlandse bericht **en** `llm_client.ask` wordt niet aangeroepen
  (assert op de mock)
- `compose_answer` met `result.found=True` → `llm_client.ask` wordt
  precies één keer aangeroepen met een prompt gebaseerd op
  `build_answer_context(result)`
- statische promptcheck: `007-answer-formatter.md` bevat de substring
  "Nederlands" en bevat geen instructie die om aanbevelingen/advies vraagt
  (regressietest tegen ongemerkte prompt-drift, aangezien "altijd
  Nederlands" verder niet deterministisch af te dwingen is op LLM-output)
