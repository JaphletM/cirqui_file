# ISSUE-3: Bedrijven en definities ophalen uit MongoDB (incl. intersectie)

## User story

Als Jeroen wil ik, wanneer ik naar één technologie vraag, de bedrijven of
de definitie ervan terugkrijgen; en wanneer ik naar meerdere technologieën
tegelijk vraag, wil ik alleen de bedrijven zien die ze **allemaal**
gebruiken.

## Depends on

ISSUE-2 (levert `resolve_query_terms` output: bevestigde term-matches per
opgegeven term) en ISSUE-1 (`QueryIntent.intent` bepaalt welk type
lookup nodig is).

## Business rules covered

- "Welke bedrijven gebruiken X" → bedrijvenlijst uit MongoDB.
- "Wat is X" → definitie (uit de Qdrant-payload, al aanwezig na ISSUE-2 —
  geen extra Mongo-call nodig voor dit type).
- Samengestelde vraag → alleen bedrijven die in **alle** termlijsten
  voorkomen (intersectie), exact zoals het voorbeeld in
  `docs/chatbot-userstory.md`: Kubernetes ∩ Java ∩ Linux → `[Google]`.

## Proposed file tree

```
src/Savers/
  MongoSaver.py                      # UITBREIDEN — find_companies_for_term toevoegen

src/Extractors/
  TermMatcher.py                     # UITBREIDEN — intersect_companies toevoegen

src/Workflows/
  ChatbotWorkflow.py                 # UITBREIDEN — gather_query_results toevoegen

tests/Savers/
  test_mongo_saver_companies.py      # NIEUW
tests/Extractors/
  test_term_matcher.py               # UITBREIDEN (intersect_companies tests)
```

## Functions

### `find_companies_for_term(term_name: str) -> list[str]` — `src/Savers/MongoSaver.py`

- **Verantwoordelijkheid:** de `companies`-lijst ophalen voor een exacte
  termnaam (zoals opgeslagen door `save_new_terms`, dat `companies` vult
  via `$addToSet`).
- **Input:** `term_name: str` (de al-gematchte, exacte term uit Qdrant —
  niet de ruwe gebruikersinput).
- **Output:** `list[str]` — lege lijst als de term geen `companies`-veld
  heeft (bijv. via de JSON-fallback, die dit veld niet altijd zet — zie
  `save_terms_to_json`).
- **Failures:** bij `PyMongoError` terugvallen op de bestaande
  JSON-fallback (`load_terms_from_json`), consistent met
  `load_existing_terms`. Geen andere silent defaults: als de term zelf
  niet bestaat, is dat een normaal "niet gevonden"-resultaat, geen fout.
- **Dependencies:** `get_terms_collection`, `load_terms_from_json` (fallback).
- **Business rule of I/O:** infrastructuur (data access).

### `intersect_companies(companies_per_term: dict[str, list[str]]) -> list[str]` — `src/Extractors/TermMatcher.py`

- **Verantwoordelijkheid:** voor een `samengesteld`-vraag bepalen welke
  bedrijven in **elke** termlijst voorkomen.
- **Input:** `companies_per_term: dict[str, list[str]]`.
- **Output:** `list[str]`, deterministisch geordend (bijv. op volgorde
  van de eerste termlijst).
- **Failures:** geen (pure functie).
  - leeg dict → `[]`
  - één term met een lege bedrijvenlijst → `[]` (er kan dan niets in
    "alle" lijsten voorkomen)
- **Dependencies:** geen.
- **Business rule of I/O:** business rule, pure en testbaar zonder Mongo.

### `gather_query_results(intent: QueryIntent, resolved_terms: dict[str, list[dict]]) -> QueryResult` — `src/Workflows/ChatbotWorkflow.py`

- **Verantwoordelijkheid:** orkestratie — vertaalt het intent-type naar de
  juiste lookup:
  - `definitie`: pak de definitie rechtstreeks uit de (enige) bevestigde
    Qdrant-match in `resolved_terms` — geen Mongo-call nodig.
  - `bedrijven`: roep `find_companies_for_term` aan voor de ene
    bevestigde term.
  - `samengesteld`: roep `find_companies_for_term` aan per term, dan
    `intersect_companies`.
- **Input:** `QueryIntent`, `resolved_terms` (van `resolve_query_terms`).
- **Output:** `QueryResult` (domain object, formeel gedefinieerd in
  ISSUE-4; hier al gebruikt met velden `intent`, `terms`, `found: bool`,
  `companies: list[str] | None`, `definitions: dict[str, str] | None`).
  `found` is `False` zodra een term geen bevestigde match had, of — bij
  `samengesteld` — de intersectie leeg is.
- **Failures:** propageert infrastructuurfouten van `find_companies_for_term`.
- **Dependencies:** `find_companies_for_term`, `intersect_companies`.
- **Business rule of I/O:** orkestratie.

## Required tests

- `intersect_companies` met het exacte voorbeeld uit
  `docs/chatbot-userstory.md`:
  `{"Kubernetes": ["Google","ASML"], "Java": ["Google","Booking"], "Linux": ["Google","ASML","Booking"]}`
  → `["Google"]`
- `intersect_companies({})` → `[]`
- `intersect_companies` met één term die een lege lijst heeft → `[]`
- `intersect_companies` met één enkele term → geeft die termlijst terug ongewijzigd
- `find_companies_for_term`: gemockt Mongo-document zonder `companies`-key
  → `[]` (geen `KeyError`)
- `find_companies_for_term`: gemockte `PyMongoError` → valt terug op JSON
- `gather_query_results` voor `bedrijven`-intent zonder bevestigde match
  (leeg uit ISSUE-2) → `QueryResult(found=False, ...)`
- `gather_query_results` voor `samengesteld`-intent met lege intersectie
  → `QueryResult(found=False, ...)`
