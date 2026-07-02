# ISSUE-3: Bedrijven en definities ophalen uit MongoDB (incl. intersectie)

## User story

**Epic:** Als CEO wil ik vragen kunnen stellen over het technische
landschap van een klant, zodat ik hen vaardige mensen kan aanbieden.

Dit issue behandelt daarvan de daadwerkelijke opzoeking: wanneer ik naar
één technologie vraag, wil ik de bedrijven of de definitie ervan
terugkrijgen; en wanneer ik naar meerdere technologieën tegelijk vraag,
wil ik zowel zien welke bedrijven élke term apart gebruiken, als welke
bedrijven ze **allemaal samen** gebruiken — zonder dat het systeem voor
mij raadt welke van de twee ik bedoelde.

## Depends on

ISSUE-2 (levert `resolve_query_terms` output: bevestigde term-matches per
opgegeven term) en ISSUE-1 (`QueryIntent.intent` bepaalt welk type
lookup nodig is; `bedrijven` staat 1 of meer termen toe, zie ISSUE-1).

## Business rules covered

- "Welke bedrijven gebruiken X" → bedrijvenlijst uit MongoDB.
- "Wat is X" (of "wat is X, Y en Z") → definitie per term (uit de
  Qdrant-payload, al aanwezig na ISSUE-2 — geen extra Mongo-call nodig
  voor dit type). Bij meerdere termen krijgt elke term zijn eigen
  definitie; er is hier geen intersectie-vraagstuk zoals bij `bedrijven`,
  dus geen aparte scope-afweging nodig (zie ISSUE-1).
- Bij meerdere termen in een `bedrijven`-vraag: **altijd beide**
  teruggeven — de bedrijvenlijst per term, én de intersectie (bedrijven
  die alle opgegeven termen gebruiken). Het systeem kiest niet zelf welke
  interpretatie de User bedoelde; dat gebeurt pas bij het formuleren
  van het antwoord (ISSUE-4), op basis van wat nuttig is om te tonen.
  Voorbeeld uit `docs/chatbot-userstory.md`: bij Kubernetes, Java, Linux
  krijg je zowel de losse lijsten per term als de intersectie `[Google]`.

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

- **Verantwoordelijkheid:** bepalen welke bedrijven in **elke** termlijst
  voorkomen. Wordt aangeroepen zodra een `bedrijven`-vraag 2 of meer
  termen heeft — niet gekoppeld aan een apart intent-type (zie ISSUE-1).
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
  - `definitie`: pak voor **elke** term in `intent.terms` de definitie
    rechtstreeks uit de bijbehorende bevestigde Qdrant-match in
    `resolved_terms` en bouw `definitions` (`dict[str, str]`) — geen
    Mongo-call nodig. Een term zonder bevestigde match krijgt geen entry
    in `definitions` (niet een lege string — dat zou een gevonden-maar-
    lege definitie suggereren, wat niet hetzelfde is als "niet gevonden").
  - `bedrijven`: roep `find_companies_for_term` aan voor **elke**
    bevestigde term in `intent.terms` en bouw `companies_per_term`
    (`dict[str, list[str]]`). Als `len(intent.terms) >= 2`, bereken
    daarnaast altijd `companies_intersection` via `intersect_companies`.
    Bij precies 1 term blijft `companies_intersection` `None` (intersectie
    van één lijst is triviaal en voegt niets toe).
- **Input:** `QueryIntent`, `resolved_terms` (van `resolve_query_terms`).
- **Output:** `QueryResult` (domain object, formeel gedefinieerd in
  ISSUE-4; hier al gebruikt met velden `intent`, `terms`, `found: bool`,
  `companies_per_term: dict[str, list[str]] | None`,
  `companies_intersection: list[str] | None`,
  `definitions: dict[str, str] | None`).
  `found` is `True` zodra **minstens één** term een niet-lege
  bedrijvenlijst of definitie opleverde — niet pas wanneer alles gevonden
  is. Een deelresultaat (bijv. Kubernetes gevonden, Java niet) is nog
  steeds nuttige informatie voor de User en telt dus als "gevonden"; welke
  termen precies niets opleverden staat gewoon in `companies_per_term`
  als lege lijst per term, zodat ISSUE-4 dat expliciet kan benoemen in
  plaats van het te verzwijgen.
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
- `gather_query_results` voor `bedrijven`-intent met 1 term zonder
  bevestigde match (leeg uit ISSUE-2) → `QueryResult(found=False, ...)`,
  `companies_intersection is None`
- `gather_query_results` voor `bedrijven`-intent met 3 termen (Kubernetes,
  Java, Linux, zoals het voorbeeld in de userstory) → `companies_per_term`
  bevat alle drie de losse lijsten, `companies_intersection == ["Google"]`,
  `found is True`
- `gather_query_results` voor `bedrijven`-intent met 2 termen waarvan er
  één niets oplevert (bijv. Kubernetes gevonden, "Foo" niet) → `found is
  True` (Kubernetes-resultaat telt), `companies_per_term["Foo"] == []`,
  `companies_intersection == []` (kan niet overlappen met een lege lijst)
- `gather_query_results` voor `bedrijven`-intent waarbij **geen enkele**
  term iets oplevert → `found is False`
- `gather_query_results` voor `definitie`-intent met 3 termen (Kubernetes,
  Java, Linux) waarvan er 2 een bevestigde Qdrant-match hebben → 
  `definitions` bevat exact die 2 termen met hun definitie, de derde term
  ontbreekt in de dict (geen lege string), `found is True`
- `gather_query_results` voor `definitie`-intent waarbij geen enkele term
  een bevestigde match heeft → `definitions == {}`, `found is False`
