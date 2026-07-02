# ISSUE-0: App-configuratie — pytest als testrunner opzetten

## Waarom dit een los issue is

`cirqui-skills/skills/app-configuration.md` schrijft expliciet voor:
*"Do not add feature code while performing application configuration"* en
*"Show the proposed configuration files and dependencies before changing
them."* ISSUE-1 introduceert de eerste `tests/`-map van het project en
heeft dus een werkende testrunner nodig — maar het opzetten van die
runner is zelf geen feature-code en hoort dus niet stilzwijgend in
ISSUE-1 te zitten. Dit issue is de voorwaarde voor ISSUE-1 t/m ISSUE-5:
zonder dit is er geen manier om de "Required tests" uit die issues
daadwerkelijk te draaien.

## Depends on

Niets. Moet vóór ISSUE-1 worden gedaan.

## Required analysis (per app-configuration.md)

- **Taal/framework:** Python 3 (lokaal geverifieerd: 3.14.3).
- **Package manager:** geen enkele aanwezig in de repo-root — geen
  `requirements.txt`, `pyproject.toml` of `Pipfile`. Dependencies staan
  nergens vastgelegd; ze zijn alleen lokaal geïnstalleerd. Dat is de
  kern van wat dit issue oplost.
- **Entry point:** `src/Main.py`.
- **Productie-dependencies (lokaal geverifieerd geïnstalleerd, nog niet
  vastgelegd):**
  - `pymongo==4.17.0`
  - `qdrant-client==1.18.0`
  - `openai==2.38.0`
  - `python-dotenv==1.2.2`
  - `bleach==6.3.0`
- **Development-dependency:** `pytest==9.0.3` (al lokaal aanwezig, maar
  ook niet vastgelegd).
- **Testrunner:** pytest, testmap `tests/`, mirrorend op `src/` (per
  `file-structure.md`: "Place tests according to the selected language's
  project convention").
- **Omgevingsvariabelen:** `OPENAI_API_KEY`, `OPENROUTER_API_KEY` (zie
  `Services/LLMclient.py`, `Services/EmbeddingService.py`), geladen via
  `python-dotenv` uit `.env`. Er is geen `.env.example` in de repo.
- **Externe services:** MongoDB (`localhost:27017`), Qdrant
  (`localhost:6333`) — beide vereist een lokaal draaiende instantie voor
  integratietests; unit tests op de domeinlaag (per `function-
  definitions.md`: "Business functions can be tested without external
  infrastructure") mogen hier niet van afhangen.

## Proposed file tree

```
requirements.txt              # NIEUW — productie-dependencies, gepind
requirements-dev.txt          # NIEUW — pytest, gescheiden van productie
.env.example                  # NIEUW — voorbeeldwaarden, geen echte secrets
pytest.ini                    # NIEUW — testpad-config (rootdir, testpaths=tests)
tests/
  __init__.py                 # NIEUW (indien nodig voor import-resolutie)
```

## Proposed content

**`requirements.txt`**
```
pymongo==4.17.0
qdrant-client==1.18.0
openai==2.38.0
python-dotenv==1.2.2
bleach==6.3.0
```

**`requirements-dev.txt`**
```
-r requirements.txt
pytest==9.0.3
```

**`.env.example`**
```
OPENAI_API_KEY=
OPENROUTER_API_KEY=
```

**`pytest.ini`**
```ini
[pytest]
testpaths = tests
pythonpath = src
```

(`pythonpath = src` zodat `from Extractors.QueryIntentExtractor import ...`
werkt zonder dat elke testfile zelf `sys.path` moet aanpassen — consistent
met hoe `src/Main.py` en de bestaande modules elkaar al importeren.)

## Commands (te documenteren in README)

- Installeren: `pip install -r requirements-dev.txt`
- Tests draaien: `pytest`

## Validation (per app-configuration.md)

- Een schone checkout kan dependencies installeren met het gedocumenteerde
  commando.
- `pytest` (zonder argumenten) vindt en draait `tests/Extractors/
  test_query_intent_extractor.py` succesvol vanuit de repo-root.
- Ontbrekende `OPENAI_API_KEY`/`OPENROUTER_API_KEY` geven een duidelijke
  fout bij het starten van de app (niet een stille crash dieper in de
  call-stack) — dit is nu **niet** het geval (`LLMClient.__init__` en
  `EmbeddingService`'s module-level `OpenAI(api_key=os.getenv(...))`
  falen pas bij de eerste API-call, niet bij opstarten). Buiten scope om
  hier te fixen, maar wel genoteerd als bestaande afwijking van de
  skill-eis "Validate required configuration when the application
  starts."
- Geen secrets gecommit — `.env` staat al in `.gitignore` (geverifieerd:
  regel 151), alleen `.env.example` wordt toegevoegd.
