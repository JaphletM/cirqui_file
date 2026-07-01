# ISSUE-1: Intentie en termen herkennen uit een natuurlijke taalvraag

## User story

Als Jeroen (CEO, niet-technisch) wil ik een vraag in gewone taal kunnen
stellen, zodat het systeem automatisch begrijpt wat ik zoek (bedrijven,
een definitie, of meerdere termen tegelijk) zonder dat ik zoeksyntax hoef
te kennen.

## Depends on

Niets (eerste stap in de pipeline).

## Business rules covered

- Zoeken is alleen mogelijk op basis van herkende termen (garbage/onduidelijke
  vragen mogen niet stilzwijgend doorstromen naar de zoekstap).
- De chatbot informeert alleen — deze stap classificeert een vraag, ze
  neemt geen beslissingen namens Jeroen.

## Scope-beslissing (expliciet, geen aanname zonder onderbouwing)

`docs/chatbot-userstory.md` beschrijft drie vraagtypes. Om dubbelzinnige
combinaties te vermijden leggen we de cardinaliteit per intent vast:

| intent        | aantal termen | voorbeeld                                   |
|---------------|----------------|----------------------------------------------|
| `bedrijven`   | exact 1        | "Welke bedrijven gebruiken Kubernetes?"       |
| `definitie`   | exact 1        | "Wat is Kubernetes?"                          |
| `samengesteld`| 2 of meer      | "Welke bedrijven gebruiken Kubernetes, Java en Linux?" |

Deze cardinaliteit is een domein-invariant en wordt afgedwongen in
`validate_intent` (zie hieronder), niet overgelaten aan het LLM.

## Proposed file tree

```
data/prompts/
  006-query-intent.md                # NIEUW - prompt template voor intent-extractie

src/Extractors/
  QueryIntentExtractor.py            # NIEUW

tests/Extractors/
  test_query_intent_extractor.py     # NIEUW
```

> Er bestaat nog geen `tests/`-map in het project. Dit issue introduceert de
> eerste testmap (pytest, mirrorend op `src/`). Voeg `pytest` toe als
> dev-dependency als dat nog niet gebeurd is.

## Functions

### `QueryIntent` (dataclass, domain)

- **Verantwoordelijkheid:** valide, afgedwongen representatie van een
  geclassificeerde vraag.
- **Velden:** `intent: str` (`"bedrijven" | "definitie" | "samengesteld"`),
  `terms: list[str]`.
- **Bevat geen I/O.**

### `validate_intent(raw: dict) -> QueryIntent`

- **Verantwoordelijkheid:** onvertrouwde LLM-JSON-output valideren en
  omzetten naar een `QueryIntent`. Business rule / boundary validation.
- **Input:** `raw: dict` — geparste JSON van het LLM-antwoord.
- **Output:** `QueryIntent`.
- **Failures (expliciet, geen silent defaults):**
  - `raw["intent"]` ontbreekt of niet in de toegestane set →
    `InvalidQueryIntentError("intent", raw.get("intent"))`
  - `raw["terms"]` ontbreekt, is geen lijst, is leeg, of bevat een
    lege/whitespace-only string → `InvalidQueryIntentError("terms", ...)`
  - cardinaliteit klopt niet met de tabel hierboven →
    `InvalidQueryIntentError("terms", ...)` met duidelijke boodschap
    ("definitie verwacht exact 1 term, kreeg N")
- **Dependencies:** geen (pure functie, geen infrastructuur).
- **Business rule of I/O:** business rule (domain invariant).

### `extract_query_intent(question: str, llm_client, prompt_template: str) -> QueryIntent`

- **Verantwoordelijkheid:** de vraag naar het LLM sturen, JSON-respons
  parsen, en via `validate_intent` valideren. Analoog aan het bestaande
  patroon in `extract_technical_terms`.
- **Input:** `question: str`, `llm_client` (bestaande `LLMClient`),
  `prompt_template: str` (uit `006-query-intent.md`).
- **Output:** `QueryIntent`.
- **Failures:**
  - ongeldige/onparsebare JSON van het LLM → raise
    `QueryIntentParseError(raw_response)` (**niet** stilzwijgend een lege
    default teruggeven — dit wijkt bewust af van het bestaande patroon in
    `extract_technical_terms`, dat bij een parse-fout `[]` teruggeeft; dat
    patroon overtreedt de validation-skill regel "never silently replace
    invalid values with defaults" en moet hier niet herhaald worden).
  - validatiefouten van `validate_intent` propageren ongewijzigd.
- **Dependencies:** `llm_client.ask`, `validate_intent`.
- **Business rule of I/O:** I/O boundary (LLM-aanroep), delegeert
  validatie naar de pure functie.

## Prompt: `data/prompts/006-query-intent.md`

Moet het LLM instrueren om **uitsluitend** valide JSON terug te geven in
de vorm:

```json
{"intent": "bedrijven", "terms": ["Kubernetes"]}
```

en de drie toegestane intent-waarden en hun cardinaliteit expliciet
benoemen, zodat het model zich aan de scope-beslissing hierboven houdt.

## Required tests

- geldige input (`bedrijven`, 1 term) → correcte `QueryIntent`
- geldige input (`samengesteld`, 3 termen) → correcte `QueryIntent`
- ontbrekende `terms`-key → `InvalidQueryIntentError` noemt veld `terms`
- lege `terms`-lijst → raises
- `terms` bevat een lege string → raises
- onbekende `intent`-waarde → `InvalidQueryIntentError` noemt veld `intent`
- `bedrijven` met 2 termen → raises (cardinaliteitsregel)
- `definitie` met 2 termen → raises (cardinaliteitsregel)
- `samengesteld` met 1 term → raises (cardinaliteitsregel)
- `extract_query_intent` met LLM-mock die niet-JSON teruggeeft →
  `QueryIntentParseError`, geen stille lege default
