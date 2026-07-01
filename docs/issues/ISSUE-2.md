# ISSUE-2: Termen semantisch matchen in Qdrant

## User story

Als Jeroen wil ik dat het systeem de term(en) uit mijn vraag herkent,
zelfs als ik een spelfout maak of niet de exacte naam gebruik, zodat ik
niet precies hoef te weten hoe een term in de database staat.

## Depends on

ISSUE-1 (levert een gevalideerde `QueryIntent` met `terms: list[str]`).

## Business rules covered

- Zoeken is hoofdletter-ongevoelig.
- Zoeken tolereert spelfouten via semantisch zoeken.
- Alleen technische termen die al in de database staan zijn doorzoekbaar
  (een term zonder voldoende gelijkende match telt als "niet gevonden",
  niet als een gok).

## Proposed file tree

```
src/Extractors/
  TermMatcher.py                     # NIEUW — pure domain helpers

src/Savers/
  QdrantSaver.py                     # UITBREIDEN — search_matching_terms toevoegen

src/Workflows/
  ChatbotWorkflow.py                 # NIEUW — resolve_query_terms (eerste functie in dit bestand)

tests/Extractors/
  test_term_matcher.py               # NIEUW
tests/Savers/
  test_qdrant_saver_search.py        # NIEUW
tests/Workflows/
  test_chatbot_workflow.py           # NIEUW (uitgebreid in latere issues)
```

## Functions

### `normalize_term(term: str) -> str` — `src/Extractors/TermMatcher.py`

- **Verantwoordelijkheid:** een term herleiden tot een vergelijkbare vorm
  (lowercase, getrimd) zodat matching hoofdletter-ongevoelig is.
- **Input:** `term: str`. **Output:** `str`.
- **Failures:** geen (zuivere transformatie).
- **Dependencies:** geen.
- **Business rule of I/O:** business rule (case-insensitiviteit).

### `search_matching_terms(query_term: str, limit: int = 5) -> list[dict]` — `src/Savers/QdrantSaver.py`

- **Verantwoordelijkheid:** kandidaat-termen ophalen uit de
  `technical_knowledge`-collectie voor een los stuk tekst. Hergebruikt de
  bestaande `search_similar_terms` (embed + `query_points`), maar geeft
  meerdere kandidaten mét score terug in plaats van er impliciet één te
  kiezen.
- **Input:** `query_term: str`, `limit: int`.
- **Output:** `list[dict]`, elk `{"term": str, "definition": str, "score": float}`.
- **Failures:** infrastructuurfouten (Qdrant onbereikbaar) propageren als
  de onderliggende client-exceptie — geen silent fallback naar een lege
  lijst, want dat zou "geen resultaten" onterecht laten lijken op "term
  bestaat niet".
- **Dependencies:** `embed_text` (EmbeddingService), Qdrant `client`.
- **Business rule of I/O:** infrastructuur (data access).

### `select_confident_matches(candidates: list[dict], threshold: float = 0.80) -> list[dict]` — `src/Extractors/TermMatcher.py`

- **Verantwoordelijkheid:** uit ruwe Qdrant-kandidaten bepalen welke
  scores hoog genoeg zijn om als "gevonden" te tellen. Dit is dezelfde
  business-regel die al inline in `find_existing_term` (QdrantSaver)
  zit met `threshold=0.80` — die regel hoort hier gecentraliseerd te
  worden zodat hij niet dubbel gedefinieerd staat (validation-skill:
  "Do not duplicate the same rule ... Derive ... in one shared domain
  function"). **Refactor-taak binnen dit issue:** laat
  `QdrantSaver.find_existing_term` deze functie hergebruiken in plaats
  van zijn eigen inline `if results and results[0].score >= threshold`.
- **Input:** `candidates: list[dict]` (van `search_matching_terms`),
  `threshold: float`.
- **Output:** `list[dict]` — subset van `candidates` met `score >= threshold`.
- **Failures:** geen (zuivere filterfunctie); lege input → lege output.
- **Dependencies:** geen.
- **Business rule of I/O:** business rule (matchdrempel), pure en
  testbaar zonder Qdrant.

### `resolve_query_terms(intent: QueryIntent) -> dict[str, list[dict]]` — `src/Workflows/ChatbotWorkflow.py`

- **Verantwoordelijkheid:** orkestratie — voor elke term in `intent.terms`:
  normaliseren → `search_matching_terms` → `select_confident_matches`.
- **Input:** `QueryIntent` (uit ISSUE-1).
- **Output:** `dict[str, list[dict]]` — map van originele term naar zijn
  bevestigde matches (kan leeg zijn per term als niets de drempel haalt).
- **Failures:** propageert infrastructuurfouten van `search_matching_terms`.
- **Dependencies:** `normalize_term`, `search_matching_terms`,
  `select_confident_matches`.
- **Business rule of I/O:** orkestratie (combineert domain + infra,
  hoort in de workflow-laag, niet in de domeinlaag).

## Required tests

- `normalize_term("  Kubernetes ")` → `"kubernetes"`
- `normalize_term("KUBERNETES")` → `"kubernetes"`
- `select_confident_matches` met score 0.95 en threshold 0.80 → bevat kandidaat
- `select_confident_matches` met score 0.50 → kandidaat uitgesloten
- `select_confident_matches` met score exact 0.80 → bevat kandidaat (boundary-waarde)
- `select_confident_matches([])` → `[]`
- `resolve_query_terms` met gemockte `search_matching_terms`: term zonder
  kandidaat boven de drempel → lege lijst voor die term (traceerbaar naar
  de "geen resultaten"-regel later in de pipeline)
- refactor-check: `find_existing_term` roept `select_confident_matches`
  aan (geen losstaande duplicaat-drempelcheck meer in `QdrantSaver.py`)
