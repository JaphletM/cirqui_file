# ISSUE-1: Intentie en termen herkennen uit een natuurlijke taalvraag

## User story

**Epic:** Als CEO wil ik vragen kunnen stellen over het technische
landschap van een klant, zodat ik hen vaardige mensen kan aanbieden.

Dit issue behandelt de eerste stap daarvan: mijn vraag in gewone taal
wordt automatisch begrepen — als een vraag naar bedrijven, naar een
definitie, of naar meerdere termen tegelijk — zonder dat ik zoeksyntax
hoef te kennen.

## Depends on

Niets (eerste stap in de pipeline).

## Business rules covered

- Zoeken is alleen mogelijk op basis van herkende termen (garbage/onduidelijke
  vragen mogen niet stilzwijgend doorstromen naar de zoekstap).
- De chatbot informeert alleen — deze stap classificeert een vraag, ze
  neemt geen beslissingen namens de User.

## Scope-beslissing (expliciet, geen aanname zonder onderbouwing)

`docs/chatbot-userstory.md` beschrijft drie vraagtypes, waarvan er twee
(bedrijven-lookup en de samengestelde/intersectie-lookup) in de praktijk
dezelfde vraag zijn met een verschillend aantal termen: "welke bedrijven
gebruiken Kubernetes?" en "welke bedrijven gebruiken Kubernetes, Java en
Linux?" zijn beide een `bedrijven`-vraag — alleen het aantal termen
verschilt. Er is dus **geen aparte `samengesteld`-intent meer nodig**: dat
zou het LLM dwingen een classificatiebeslissing te maken (intersectie
bedoeld, of gewoon losse termen opsommen?) die achteraf net zo goed puur
op het aantal termen kan worden afgeleid, zonder risico op een verkeerde
classificatie bij dubbelzinnige formuleringen.

We houden twee intents over, allebei zonder harde cardinaliteitsgrens:

| intent      | aantal termen | voorbeeld                                              |
|-------------|----------------|---------------------------------------------------------|
| `bedrijven` | 1 of meer      | "Welke bedrijven gebruiken Kubernetes?" / "...Kubernetes, Java en Linux?" |
| `definitie` | 1 of meer      | "Wat is Kubernetes?" / "Wat is Kubernetes, Java en Linux?" |

Bij `bedrijven` met meerdere termen wordt **altijd zowel** de
bedrijvenlijst per term **als** de intersectie (bedrijven die alle
opgegeven termen gebruiken) berekend en teruggegeven — zie ISSUE-3. De
keuze welke framing het antwoord krijgt (per term, of de overlap
benadrukken) ligt bij de antwoord-formattering in ISSUE-4, niet bij de
intent-classificatie hier. Dat voorkomt dat een vraag als "welke
bedrijven gebruiken Kubernetes en Java?" (die zowel "beide apart" als
"het snijvlak" kan betekenen) al bij de intentherkenning fout wordt
geïnterpreteerd.

Bij `definitie` met meerdere termen ("Wat is Kubernetes, Java en Linux?")
is er, anders dan bij `bedrijven`, geen alternatieve interpretatie
mogelijk — er wordt altijd gewoon de definitie van elke genoemde term
teruggegeven. Daarom is hier geen aparte scope-afweging nodig: de
cardinaliteitsgrens van exact 1 term wordt losgelaten, puur om
consistent te zijn met `bedrijven` en omdat er geen reden is om een
vraag met meerdere termen te weigeren.

Er geldt geen harde cardinaliteitsgrens meer die in `validate_intent`
afgedwongen hoeft te worden (zie hieronder) — alleen de generieke regel
dat `terms` niet leeg mag zijn.

## Proposed file tree

```
data/prompts/
  006-query-intent.md                # NIEUW - prompt template voor intent-extractie

src/Extractors/
  QueryIntentExtractor.py            # NIEUW

tests/Extractors/
  test_query_intent_extractor.py     # NIEUW
```

> Er bestaat nog geen `tests/`-map in het project. Dit issue introduceert
> de eerste testmap (pytest, mirrorend op `src/`). `pytest` staat al
> lokaal geïnstalleerd (geverifieerd), maar nergens in de repo als
> dependency vastgelegd — dat vastleggen (bijv. `requirements-dev.txt`)
> hoort niet bij de feature-code van dit issue en moet los opgepakt
> worden.

## Functions

### `QueryIntent` (dataclass, domain)

- **Verantwoordelijkheid:** valide, afgedwongen representatie van een
  geclassificeerde vraag.
- **Velden:** `intent: str` (`"bedrijven" | "definitie"`), `terms: list[str]`.
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
    (dit geldt voor beide intents — geen aparte cardinaliteitsregel meer
    nodig sinds `definitie` ook meerdere termen toestaat)
- **Dependencies:** geen (pure functie, geen infrastructuur).
- **Business rule of I/O:** business rule (domain invariant).

### `extract_query_intent(question: str, llm_client, prompt_template: str) -> QueryIntent`

- **Verantwoordelijkheid:** de vraag naar het LLM sturen, JSON-respons
  parsen, en via `validate_intent` valideren. Volgt hetzelfde patroon als
  het bestaande `extract_technical_terms` (LLM-call + JSON-parse), maar
  is geen duplicaat: andere prompt, ander doel (intent-classificatie
  i.p.v. termextractie) en een ander eind-domeinobject (`QueryIntent` vs.
  een lijst termen). Er is geen bestaande functie die hergebruikt kan
  worden voor deze specifieke taak.
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

en de twee toegestane intent-waarden benoemen. Instrueer expliciet dat:
- een opsomming van meerdere technologieën bij een "welke bedrijven"-vraag
  **altijd** intent `bedrijven` met alle genoemde termen in `terms`
  oplevert — het LLM hoeft dus niet zelf te bepalen of een intersectie
  bedoeld is;
- een opsomming van meerdere technologieën bij een "wat is"-vraag
  **altijd** intent `definitie` met alle genoemde termen in `terms`
  oplevert (bijv. "Wat is Kubernetes, Java en Linux?" →
  `{"intent": "definitie", "terms": ["Kubernetes", "Java", "Linux"]}`).

## Required tests

- geldige input (`bedrijven`, 1 term) → correcte `QueryIntent`
- geldige input (`bedrijven`, 3 termen) → correcte `QueryIntent` (meerdere
  termen zijn toegestaan, geen aparte intent nodig)
- geldige input (`definitie`, 1 term) → correcte `QueryIntent`
- geldige input (`definitie`, 3 termen, bijv. Kubernetes/Java/Linux) →
  correcte `QueryIntent` (geen cardinaliteitsgrens meer)
- ontbrekende `terms`-key → `InvalidQueryIntentError` noemt veld `terms`
- lege `terms`-lijst → raises
- `terms` bevat een lege string → raises
- onbekende `intent`-waarde → `InvalidQueryIntentError` noemt veld `intent`
- `extract_query_intent` met LLM-mock die niet-JSON teruggeeft →
  `QueryIntentParseError`, geen stille lege default
