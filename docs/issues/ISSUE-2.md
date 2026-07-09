# ISSUE-2: Termen semantisch matchen in Qdrant

## User story

**Epic:** Als CEO wil ik vragen kunnen stellen over het technische
landschap van een klant, zodat ik hen vaardige mensen kan aanbieden.

Dit issue behandelt daarvan het onderdeel matching: het systeem herkent
de term(en) uit mijn vraag, ook als ik een spelfout maak of niet de
exacte naam gebruik, zodat ik niet precies hoef te weten hoe een term in
de database staat.

## Depends on

ISSUE-1 (levert een gevalideerde `QueryIntent` met `terms: list[str]`).

## Business rules covered

- Zoeken is hoofdletter-ongevoelig.
- Zoeken tolereert spelfouten via semantisch zoeken.
- Alleen technische termen die al in de database staan zijn doorzoekbaar
  (een term zonder voldoende gelijkende match telt als "niet gevonden",
  niet als een gok).

## Bestaande functies hergebruikt (geen duplicaten aangemaakt)

Voor dit issue was er een concreet duplicatierisico: het lag voor de
hand om een nieuwe `search_matching_terms`-functie in `QdrantSaver.py`
te maken die intern embed + `client.query_points` aanroept — maar dat is
vrijwel exact wat de **bestaande** `search_similar_terms(query_text,
limit=5)` (QdrantSaver.py) al doet. Het enige verschil zou de vorm van
de output zijn (`ScoredPoint`-objecten vs. platte dicts). Dat is geen
reden voor een tweede, bijna-identieke infrastructuurfunctie — de
reshaping naar dicts gebeurt hieronder in de orkestratielaag, niet in
een nieuwe Qdrant-functie. `search_similar_terms` wordt dus **rechtstreeks
hergebruikt**, niet gedupliceerd.

Daarnaast bevat `TermComparator.find_existing_term(term_name,
existing_terms)` (bestaand, ingestion-pad) al exact de normalisatie die
dit issue nodig heeft: `term_name.lower().strip()` en
`existing_name.lower().strip()`, inline en dubbel geschreven in die ene
functie. `normalize_term` (hieronder) trekt die logica naar één gedeelde
functie; **refactor-taak binnen dit issue:** pas
`TermComparator.find_existing_term` aan zodat die `normalize_term`
gebruikt in plaats van zijn eigen inline `.lower().strip()`-aanroepen.

## Proposed file tree

```
src/Extractors/
  TermMatcher.py                     # NIEUW — pure domain helpers
  TermComparator.py                  # UITBREIDEN — hergebruikt normalize_term (refactor, geen gedragswijziging)

src/Savers/
  QdrantSaver.py                     # UITBREIDEN — find_existing_term hergebruikt select_confident_matches (refactor)

src/Workflows/
  ChatbotWorkflow.py                 # NIEUW — resolve_query_terms (eerste functie in dit bestand)

tests/Extractors/
  test_term_matcher.py               # NIEUW
  test_term_comparator.py            # NIEUW (dekt de refactor)
tests/Workflows/
  test_chatbot_workflow.py           # NIEUW (uitgebreid in latere issues)
```

> `TermMatcher.py` is een nieuw bestand in de al bestaande `Extractors/`-map
> (geen nieuwe map, conform file-structure.md). Het is bewust **niet**
> samengevoegd met `TermComparator.py`: dat bestand behandelt exacte-naam-
> vergelijking tijdens het **inladen** van termen (nieuw vs. bestaand),
> terwijl `TermMatcher.py` gaat over confidence-matching tijdens het
> **bevragen** — andere verantwoordelijkheid, andere reden om te
> veranderen (file-structure.md: "Split ... when its steps can change for
> different reasons" — geldt hier op bestandsniveau).

## Functions

### `normalize_term(term: str) -> str` — `src/Extractors/TermMatcher.py`

- **Verantwoordelijkheid:** een term herleiden tot een vergelijkbare vorm
  (lowercase, getrimd) zodat matching hoofdletter-ongevoelig is. Enige
  bron van waarheid voor deze normalisatie in de hele codebase.
- **Input:** `term: str`. **Output:** `str`.
- **Failures:** geen (zuivere transformatie).
- **Dependencies:** geen.
- **Business rule of I/O:** business rule (case-insensitiviteit).

### `select_confident_matches(candidates: list[dict], threshold: float = 0.80) -> list[dict]` — `src/Extractors/TermMatcher.py`

- **Verantwoordelijkheid:** uit ruwe Qdrant-kandidaten bepalen welke
  scores hoog genoeg zijn om als "gevonden" te tellen. Dit is dezelfde
  business-regel die al inline in `find_existing_term` (QdrantSaver) zit
  met `threshold=0.80` — die regel hoort hier gecentraliseerd te worden
  zodat hij niet dubbel gedefinieerd staat (validation-skill: "Do not
  duplicate the same rule ... Derive ... in one shared domain function").
  **Refactor-taak binnen dit issue:** laat `QdrantSaver.find_existing_term`
  deze functie hergebruiken in plaats van zijn eigen inline
  `if results and results[0].score >= threshold` — zonder de externe
  signatuur van `find_existing_term` te wijzigen (wordt ook al gebruikt
  door `CustomerAnalysisWorkflow.check_terms_in_vector_store`).
- **Input:** `candidates: list[dict]` (elk `{"term": str, "definition": str,
  "score": float}` — de reshaping van Qdrant's `ScoredPoint` naar dit
  formaat gebeurt in `resolve_query_terms`, zie hieronder), `threshold: float`.
- **Output:** `list[dict]` — subset van `candidates` met `score >= threshold`.
- **Failures:** geen (zuivere filterfunctie); lege input → lege output.
- **Dependencies:** geen.
- **Business rule of I/O:** business rule (matchdrempel), pure en
  testbaar zonder Qdrant — met platte dicts, niet met Qdrant's
  `ScoredPoint`-klasse, zodat de test geen Qdrant-import nodig heeft.

### `resolve_query_terms(intent: dict) -> dict[str, list[dict]]` — `src/Workflows/ChatbotWorkflow.py`

- **Verantwoordelijkheid:** orkestratie — voor elke term in
  `intent["terms"]`:
  1. **Eerst een exacte, hoofdletter-ongevoelige match tegen MongoDB**
     via de bestaande `TermComparator.find_existing_term` (laadt
     `existing_terms` via `load_existing_terms`). Bij een match: score
     `1.0`, klaar — **geen** Qdrant-aanroep nodig.
  2. **Alleen als er geen exacte match is**, terugvallen op semantisch
     zoeken in Qdrant met **twee varianten** van de term — de tekst
     zoals opgegeven, én `term.capitalize()` — kandidaten samenvoegen
     (bij dezelfde gevonden term de hoogste score bewaren), en dan
     `select_confident_matches` de drempel laten toepassen.
- **Waarom de exacte-match-stap nodig bleek (belangrijke bevinding,
  ontdekt na livegebruik):** termen worden bij opslag embed als
  `"term: definitie"` (`embed_term` in `EmbeddingService.py`), maar een
  zoekopdracht vanuit de chatbot embed alleen de **kale term** (de
  definitie is nu juist onbekend — dat is wat we zoeken). Die twee
  teksten zijn structureel te verschillend om een hoge similarity-score
  te halen, ook bij een perfecte naammatch. Empirisch gemeten:
  `search_similar_terms("Java")` → score 0.593, maar
  `search_similar_terms("Java: <de opgeslagen definitie>")` → score
  1.0. Dit bleek **geen randgeval**: van tien getoetste, alledaagse
  termen misten acht de drempel van 0.80, waaronder Java (0.593),
  Python (0.603), Redis (0.647) en zelfs Kubernetes (0.795 — net onder
  de grens). De exacte-match-stap via MongoDB omzeilt dit probleem
  volledig voor elke term die letterlijk (ongeacht hoofdletters)
  overeenkomt met een opgeslagen termnaam — wat de overgrote meerderheid
  van echte vragen dekt.
- **Waarom niet `normalize_term` (lowercase) vóór de Qdrant-fallback
  gebruiken:** lowercasen vóór het embedden verlaagt de score juist
  (Docker: 0.814 origineel vs. 0.565 lowercase) — vandaar de
  "probeer origineel + capitalize()"-aanpak in de Qdrant-fallback,
  in plaats van één vaste normalisatie.
- **Input:** `intent: dict` — `QueryIntent`-vorm uit ISSUE-1
  (`{"intent": str, "terms": list[str]}`).
- **Output:** `dict[str, list[dict]]` — map van originele term naar zijn
  bevestigde matches (kan leeg zijn per term als niets gevonden wordt).
- **Failures:** propageert infrastructuurfouten van `load_existing_terms`
  en `search_similar_terms`.
- **Dependencies:** `load_existing_terms` (MongoSaver),
  `find_existing_term` (TermComparator), `search_similar_terms`
  (QdrantSaver), `select_confident_matches`.
- **Business rule of I/O:** orkestratie (combineert domain + infra,
  hoort in de workflow-laag, niet in de domeinlaag).

## Bekende beperking: Qdrant-fallback onderscheidt spelfouten slecht van foute termen

De Qdrant-stap is nu alleen nog een **vangnet** voor termen zonder
exacte match (echte spelfouten/variaties) — maar dat vangnet is minder
betrouwbaar dan gehoopt. Empirisch getest, bare-term-embeddings zonder
definitie:

| vergelijking | score |
|---|---|
| "Kubernetes" vs "Kubernets" (spelfout) | 0.538 |
| "Kubernetes" vs "Docker" (compleet andere term) | 0.529 |

Deze twee liggen te dicht bij elkaar om een betrouwbare drempel op te
zetten die de ene wél en de andere niét zou doorlaten — het
embedding-model heeft bij korte, losse termen onvoldoende onderscheidend
vermogen tussen "bijna goed gespeld" en "gewoon een ander woord". Omdat
dit pad nu alleen nog als fallback dient (de meeste vragen worden al
via de exacte MongoDB-match opgelost), is de praktische impact klein,
maar puur op spelfouten vertrouwen voor de resterende gevallen blijft
onbetrouwbaar. Nog niet opgelost — zou een preciezere fuzzy-matching-
aanpak vereisen (bijv. directe stringvergelijking met een
edit-distance-drempel) in plaats van embedding-similarity, buiten de
scope van dit issue.

## Required tests

- `normalize_term("  Kubernetes ")` → `"kubernetes"`
- `normalize_term("KUBERNETES")` → `"kubernetes"`
- `select_confident_matches` met score 0.95 en threshold 0.80 → bevat kandidaat
- `select_confident_matches` met score 0.50 → kandidaat uitgesloten
- `select_confident_matches` met score exact 0.80 → bevat kandidaat (boundary-waarde)
- `select_confident_matches([])` → `[]`
- `resolve_query_terms` vindt een exacte match via MongoDB en roept
  **geen** `search_similar_terms` aan (score `1.0`)
- `resolve_query_terms`'s exacte match is hoofdletter-ongevoelig
  ("java" vindt "Java")
- `resolve_query_terms` met gemockte `search_similar_terms`: term zonder
  kandidaat boven de drempel → lege lijst voor die term (traceerbaar naar
  de "geen resultaten"-regel later in de pipeline)
- `resolve_query_terms` vindt een match als de gebruiker lowercase typt
  ("docker"), doordat ook op `.capitalize()` ("Docker") gezocht wordt
- `resolve_query_terms` zoekt maar **één keer** als de term al
  gecapitaliseerd is (geen dubbele Qdrant-aanroep voor "Kubernetes")
- `resolve_query_terms` bewaart de **hoogste** score als beide
  zoekvarianten dezelfde term opleveren met verschillende scores
- refactor-check: `find_existing_term` (QdrantSaver) roept
  `select_confident_matches` aan (geen losstaande duplicaat-drempelcheck
  meer), en `check_terms_in_vector_store` blijft ongewijzigd werken
  (regressietest op bestaand gedrag)
- refactor-check: `TermComparator.find_existing_term` roept `normalize_term`
  aan voor beide vergeleken namen (geen losstaande `.lower().strip()`
  meer in dat bestand)
