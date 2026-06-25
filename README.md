# CIRQUI – Systeemdocumentatie

---

## Plan van Aanpak

### Wat de opdracht inhoudt

In deze opdracht bouw ik een systeem dat het technische landschap van een klant onderzoekt. Het systeem verzamelt informatie uit HUMINT en WEBINT. HUMINT bestaat uit menselijke bronnen, zoals gesprekken, interviews of notities. WEBINT bestaat uit publiek beschikbare online informatie, zoals websites, vacatures en documentatie.

Het doel is om met behulp van een LLM een rapport te maken over welke technologieën, tools, platformen en systemen een klant waarschijnlijk gebruikt. Het systeem haalt ook technische termen uit de antwoorden van de LLM. Als het systeem een term nog niet kent, wordt daar extra informatie over opgezocht en opgeslagen voor later gebruik.

---

### Welke stappen ik ga ondernemen

1. De Python-code verzamelt HUMINT informatie van de gebruiker. 
2. De Python-code leest het configuratiebestand in om het juiste LLM-model te selecteren.
3. De Python-code leest de HUMINT-markdownbestanden in.
4. De Python-code leest vaste prompts in uit de prompt-directory, op numerieke volgorde.
5. De Python-code stuurt een prompt samen met de HUMINT-tekst naar het LLM.
6. Het LLM genereert een technisch landschap van de klant. Omdat het systeem gebruik maakt van Gemini via OpenRouter, maakt het LLM hierbij gebruik van Google Search grounding om actuele, publiek beschikbare informatie te verwerken. Dit vormt de WEBINT-component van het systeem.
7. De Python-code slaat het gegenereerde technische landschap op als WEBINT-bestand.
8. Met een vervolgprompt extraheert het LLM technische termen uit de gegenereerde analyse.
9. De Python-code vergelijkt de gevonden termen met bestaande termen in MongoDB.
10. Per technische term controleert het systeem of er al semantische kennis beschikbaar is in Qdrant.
11. Voor termen die nog onbekend zijn, genereert het LLM vervolgvragen en bijbehorende antwoorden.
12. De Python-code combineert per term: de definitie, de vervolgvragen en de antwoorden in één JSON-object.
13. Dit JSON-object wordt opgeslagen via `save_to_json`.
14. De Python-code slaat nieuwe termen op in MongoDB.
15. De Python-code maakt embeddings van de nieuwe termen en slaat deze op in Qdrant.
16. Het LLM genereert een volledig markdownrapport op basis van alle verzamelde klantinformatie.
17. De Python-code slaat het rapport op als markdownbestand.

---

### Welke tools en technologieën ik ga gebruiken

**Python** gebruik ik als programmeertaal. Python gebruik ik om bestanden in te lezen, data te verwerken, verbinding te maken met databases en het LLM aan te roepen.

**Gemini via OpenRouter** gebruik ik als LLM. Gemini heeft Google Search grounding ingebouwd, waardoor het bij het genereren van analyses gebruik kan maken van actuele publieke webinformatie. Hierdoor is een aparte webscraper niet nodig.

**MongoDB** gebruik ik om technische termen, LLM-antwoorden en rapporten op te slaan.

**Qdrant** gebruik ik als vector database. Hierin sla ik embeddings op van technische termen, zodat het systeem kan controleren of kennis al beschikbaar is.

**Docker** gebruik ik om MongoDB en Qdrant lokaal te draaien.

**Markdown** gebruik ik voor HUMINT-bestanden, prompttemplates en het eindrapport.

---

### Hoe ik de onderdelen ga implementeren

De HUMINT-data wordt opgeslagen in een aparte map met markdownbestanden. Het systeem leest deze bestanden in en geeft de inhoud mee aan het LLM als context.

De WEBINT-component wordt niet via een aparte scraper verzameld, maar via Gemini's ingebouwde Google Search grounding. Wanneer het systeem een prompt naar Gemini stuurt over het technische landschap van een klant, kan het model actuele publieke informatie verwerken in zijn antwoord. De output wordt opgeslagen als WEBINT-bestand via `save_webint`.

De prompts worden opgeslagen in een aparte prompt-directory. De bestandsnamen krijgen een nummer, bijvoorbeeld `001-technisch-landschap.md` en `002-termen-extraheren.md`. Het systeem laadt deze prompts in numerieke volgorde in via de Prompt Reader.

Voor technische termen die nog niet bekend zijn in Qdrant, genereert het systeem vervolgvragen via het LLM en laat het LLM deze ook direct beantwoorden. De definitie, vragen en antwoorden worden samengevoegd in één JSON-object per term.

Aan het einde worden alle verzamelde gegevens gebruikt om een volledig markdownrapport te genereren over het technische landschap van de klant.

---

### Hoe ik de prestaties ga evalueren

Ik ga het systeem evalueren door te controleren of de informatie logisch, bruikbaar en herleidbaar is.

Ik kijk of het systeem relevante informatie verwerkt uit HUMINT en of het LLM een samenhangende analyse produceert. Ook controleer ik of technische termen correct worden herkend en of definities niet dubbel worden opgeslagen.

Ik test of het iteratieve promptingproces werkt: het systeem moet na een eerste analyse automatisch vervolgvragen kunnen genereren en beantwoorden voor onbekende termen.

Verder beoordeel ik het eindrapport op volledigheid, duidelijkheid en structuur.

Voorbeeldvragen waarmee ik kan testen:

- Welke technologieën gebruikt Klant X?
- Welke cloudplatformen komen terug in de analyse?
- Welke programmeertalen worden genoemd?
- Worden technische termen correct uitgelegd?
- Gebruikt het systeem bestaande definities opnieuw in plaats van duplicaten aan te maken?

---

## Technisch Ontwerp

### Stappen in de workflow

1. Lees configuratiebestand
2. Lees HUMINT-markdownbestanden
3. Lees prompts uit prompt-directory op numerieke volgorde
4. Stuur prompt + HUMINT naar LLM (Gemini met Search grounding)
5. Sla het gegenereerde technische landschap op als WEBINT
6. Extraheer technische termen via vervolgprompt
7. Vergelijk termen met bestaande MongoDB-data
8. Controleer per term of er semantische kennis bestaat in Qdrant
9. Genereer voor onbekende termen: vervolgvragen + antwoorden via LLM
10. Sla definitie, vragen en antwoorden op als gecombineerd JSON-object
11. Sla nieuwe termen op in MongoDB
12. Genereer embeddings van nieuwe termen en sla op in Qdrant
13. Genereer eindrapport via LLM
14. Sla rapport op als markdownbestand

## Huidige implementatie

### Wat het systeem nu kan

- Een interactief CLI-menu aanbieden met twee opties: rapport genereren of HUMINT verzamelen
- HUMINT interactief verzamelen via tekst of bestandsupload, inclusief bronvermelding, informatietype en betrouwbaarheidsscore, en opslaan als JSON
- Configuratiebestand inlezen
- HUMINT-bestanden verwerken als input voor de analyseworkflow
- Prompts automatisch laden vanuit een prompt-directory op numerieke volgorde (001 t/m 005)
- Technisch landschap genereren via Gemini (met Google Search grounding als WEBINT)
- Gegenereerde WEBINT opslaan als bestand via `save_webint`
- Technische termen extraheren uit LLM-output
- Termen vergelijken met bestaande MongoDB-data
- Per term controleren of er semantische kennis beschikbaar is in Qdrant
- Vervolgvragen genereren voor onbekende termen én deze direct laten beantwoorden door het LLM
- Definitie, vragen en antwoorden samenvoegen in één JSON-object per term via `save_to_json`
- Embeddings genereren van nieuwe termen
- Embeddings opslaan in Qdrant
- Een volledig markdownrapport genereren via het LLM
- Het rapport opslaan als markdownbestand via `save_to_markdown`

Voorbeelden van gegenereerde output: APG, Coca-Cola, Educom, Ernst & Young, Google, The Social Hub.

---

## Projectarchitectuur

```
CIRQUI/
│
├── data/
│   ├── config/
│   │   └── config.txt                        – LLM-model en configuratie-instellingen
│   │
│   ├── humanInt/                             – HUMINT-bestanden per klant
│   │   ├── {bedrijf}.md                      – Handmatig aangemaakt HUMINT-bestand
│   │   └── {bedrijf}_humint.txt              – HUMINT verzameld via CollectHUMINT (JSON)
│   │
│   ├── prompts/                              – Prompttemplates op numerieke volgorde
│   │   ├── 001-technical-landscape.md
│   │   ├── 002-extract-technical-terms.md
│   │   ├── 003-generate-followup-prompts.md
│   │   ├── 004-answer-followup-questions.md
│   │   └── 005-rapport-summariser.md
│   │
│   └── webInt/                               – Gegenereerde WEBINT-bestanden per klant
│       └── {bedrijf}_webint.txt
│
├── design/
│   ├── ApplicatieStructuurDiagram.drawio
│   └── ApplicatieStructuurDiagram.png
│
└── src/
    │
    ├── database/
    │   ├── MongoDB.json                      – MongoDB configuratie
    │   └── Qdrant.json                       – Qdrant configuratie
    │
    ├── Readers/
    │   ├── ConfigReader.py                   – Leest configuratie-instellingen uit config.txt
    │   ├── PromptReader.py                   – Laadt prompts op numerieke volgorde
    │   ├── HUMIntReader.py                   – Leest HUMINT-bestanden van klanten
    │   └── CollectHUMINT.py                  – Verzamelt HUMINT interactief via CLI
    │
    ├── Services/
    │   ├── LLMclient.py                      – Stuurt prompts naar Gemini via OpenRouter
    │   └── EmbeddingService.py               – Genereert embeddings via embedding API
    │
    ├── Extractors/
    │   ├── TechnicalTermExtractor.py         – Extraheert technische termen uit LLM-output
    │   └── TermComparator.py                 – Vergelijkt termen met bestaande MongoDB-data
    │
    ├── Savers/
    │   ├── MongoSaver.py                     – Opslag van termen en analyses in MongoDB
    │   ├── QdrantSaver.py                    – Opslag van embeddings in Qdrant
    │   ├── JsonSaver.py                      – Slaat definitie, vragen en antwoorden op als JSON
    │   └── MarkdownSaver.py                  – Slaat rapporten op als markdownbestand
    │
    ├── Workflows/
    │   ├── InteractiveWorkflow.py            – CLI-menu: rapport genereren of HUMINT verzamelen
    │   └── CustomerAnalysisWorkflow.py       – Volledige analysepipeline per klant
    │
    └── output/                               – Gegenereerde bestanden per klant
        ├── {bedrijf}_analysis.json           – Technische termen, vragen en antwoorden
        └── {bedrijf}_rapport.md              – Markdownrapport
```

Voorbeelden van gegenereerde output: APG, Coca-Cola, Educom, Ernst & Young, Google, Linux, Philips, The Social Hub.

---

## Wat momenteel nog ontbreekt

De huidige versie bevat een werkende end-to-end pipeline, maar een aantal onderdelen zijn nog niet volledig geïmplementeerd.

- **Chunking** is nog niet geïmplementeerd. Teksten worden momenteel als geheel ingelezen en opgeslagen. In een volgende versie wil ik teksten automatisch opdelen in kleinere stukken voor betere embeddings en efficiëntere opslag.
- **Semantic search tijdens analyses** is nog niet actief. Qdrant wordt gebruikt voor opslag van embeddings, maar bij het genereren van analyses wordt er nog niet gezocht in Qdrant voor relevante context. Dit wil ik toevoegen zodat het systeem bestaande kennis hergebruikt tijdens het prompten.