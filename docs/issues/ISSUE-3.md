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

## Bestaande functies hergebruikt (geen duplicaten aangemaakt)

Het lag voor de hand om een nieuwe `find_companies_for_term(term_name)`
te schrijven die rechtstreeks op MongoDB queryt. Maar dat zou twee dingen
dupliceren die al bestaan:

1. **`MongoSaver.load_existing_terms()`** laadt nu al alle termen (met
   hun `companies`-veld) en heeft de `PyMongoError` → JSON-fallback al
   ingebouwd. Een nieuwe functie zou die fallback-logica opnieuw moeten
   implementeren.
2. **`TermComparator.find_existing_term(term_name, existing_terms)`**
   doet al precies de case-insensitieve naam-match die nodig is om de
   juiste term-dict uit een lijst te vinden.

In plaats van een nieuwe infrastructuurfunctie roept `gather_query_results`
daarom **eenmalig** `load_existing_terms()` aan (niet per term — één
Mongo-call voor de hele vraag, ook bij meerdere termen), en gebruikt
vervolgens `TermComparator.find_existing_term` per term om de bijbehorende
term-dict te vinden en daar `.get("companies", [])` uit te lezen. Geen
nieuwe functie in `MongoSaver.py` nodig voor dit issue.

## Proposed file tree

```
src/Extractors/
  TermMatcher.py                     # UITBREIDEN — intersect_companies toevoegen

src/Workflows/
  ChatbotWorkflow.py                 # UITBREIDEN — gather_query_results toevoegen

tests/Extractors/
  test_term_matcher.py               # UITBREIDEN (intersect_companies tests)
tests/Workflows/
  test_chatbot_workflow.py           # UITBREIDEN (gather_query_results tests)
```

> Geen wijziging aan `src/Savers/MongoSaver.py` in dit issue — zie hierboven.

## Functions

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
  juiste lookup, met hergebruik van bestaande functies:
  - `definitie`: pak voor **elke** term in `intent.terms` de definitie
    rechtstreeks uit de bijbehorende bevestigde Qdrant-match in
    `resolved_terms` en bouw `definitions` (`dict[str, str]`) — geen
    Mongo-call nodig. Een term zonder bevestigde match krijgt geen entry
    in `definitions` (niet een lege string — dat zou een gevonden-maar-
    lege definitie suggereren, wat niet hetzelfde is als "niet gevonden").
  - `bedrijven`: roep **eenmalig** `load_existing_terms()` (bestaand,
    MongoSaver) aan om alle termen te laden, en gebruik daarna per
    bevestigde term in `intent.terms` de **bestaande**
    `TermComparator.find_existing_term(term_name, existing_terms)` om de
    term-dict te vinden; lees daaruit `.get("companies", [])`. Bouw zo
    `companies_per_term` (`dict[str, list[str]]`). Als
    `len(intent.terms) >= 2`, bereken daarnaast altijd
    `companies_intersection` via `intersect_companies`. Bij precies 1
    term blijft `companies_intersection` `None` (intersectie van één
    lijst is triviaal en voegt niets toe).
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
- **Failures:** propageert infrastructuurfouten van `load_existing_terms`
  (die zelf al terugvalt op JSON bij `PyMongoError` — geen nieuwe
  foutafhandeling nodig).
- **Dependencies:** `load_existing_terms` (bestaand, MongoSaver),
  `TermComparator.find_existing_term` (bestaand), `intersect_companies`.
- **Business rule of I/O:** orkestratie.

## Required tests

- `intersect_companies` met het exacte voorbeeld uit
  `docs/chatbot-userstory.md`:
  `{"Kubernetes": ["Google","ASML"], "Java": ["Google","Booking"], "Linux": ["Google","ASML","Booking"]}`
  → `["Google"]`
- `intersect_companies({})` → `[]`
- `intersect_companies` met één term die een lege lijst heeft → `[]`
- `intersect_companies` met één enkele term → geeft die termlijst terug ongewijzigd
- `gather_query_results` voor `bedrijven`-intent: `load_existing_terms`
  wordt precies **één keer** aangeroepen, ongeacht het aantal termen in
  de vraag (regressie tegen het per-term-queryen dat expliciet vermeden is)
- `gather_query_results` met een term-dict zonder `companies`-key
  (gemockte `load_existing_terms`-output) → behandeld als `[]`, geen
  `KeyError`
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
