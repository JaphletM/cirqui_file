### Plan van Aanpak 
## Wat de opdracht inhoudt

In deze opdracht bouw ik een systeem dat het technische landschap van een klant onderzoekt. Het systeem verzamelt informatie uit HUMINT en WEBINT. HUMINT bestaat uit menselijke bronnen, zoals gesprekken, interviews of notities. WEBINT bestaat uit publiek beschikbare online informatie, zoals websites, vacatures en documentatie.

Het doel is om met behulp van een LLM een rapport te maken over welke technologieën, tools, platformen en systemen een klant waarschijnlijk gebruikt. Het systeem haalt ook technische termen uit de antwoorden van de LLM. Als het systeem een term nog niet kent, wordt daar extra informatie over opgezocht en opgeslagen voor later gebruik.

## Welke stappen ik ga ondernemen
1. Ik maak fictieve HUMINT-bestanden aan in Markdown.
2. Ik maak WEBINT-instructiebestanden aan in Markdown.
3. Ik start de CLI-agent.
4. De CLI-agent voert main.py uit.
5. main.py leest de WEBINT-instructies in.
6. De CLI-agent gebruikt Codex om publieke webinformatie op te zoeken.
7. De CLI-agent genereert een WEBINT-markdownbestand.
8. De Python-code leest de HUMINT- en WEBINT-markdownbestanden in.
9. De Python-code slaat de ruwe HUMINT- en WEBINT-informatie op in MongoDB.
10. De Pythoncode haalt de tekst op van MongoDB 
10. De Python-code splitst de tekst op in kleinere chunks.
11. De Python-code stuurt deze chunks via een API-request naar een embeddingmodel.
12. Het embeddingmodel maakt embeddings van de chunks.
13. De Python-code slaat de embeddings op in Qdrant.
14. De Python-code leest vaste prompts in uit de prompt-directory.
15. Per prompt maakt de Python-code via een API-request een embedding van de prompt.
16. De prompt-embedding wordt gebruikt om relevante context op te halen uit Qdrant.
17. De Python-code stuurt de originele prompt + opgehaalde context naar het LLM.
18. Het LLM maakt een analyse van het technische landschap van de klant.
19. De Python-code slaat deze analyse op in MongoDB.
20. Met een vervolgpunt/prompt haalt het LLM technische termen uit de analyse.
21. De Python-code controleert per technische term of er al kennis over bestaat in Qdrant.
22. Als de term bekend is, gebruikt het systeem bestaande informatie.
23. Als de term onbekend is, vraagt de Python-code extra uitleg aan het LLM.
24. Het LLM genereert generieke uitleg over de onbekende technische term.
25. De Python-code slaat deze nieuwe kennis op in MongoDB.
26. De Python-code maakt embeddings van deze nieuwe kennis en slaat die op in Qdrant.
27. Het systeem herhaalt dit proces voor vervolgprompts.
28. Uiteindelijk stuurt de Python-code alle verzamelde klantinformatie naar het LLM.
29. Het LLM genereert een markdownrapport over de WEBINT- en HUMINT-informatie van de klant.
30. De Python-code slaat het rapport op in MongoDB en eventueel als markdownbestand.
31. Het rapport wordt ook gechunked, omgezet naar embeddings en opgeslagen in Qdrant.


## Welke tools en technologieën ik ga gebruiken

Ik ga Python gebruiken als programmeertaal. Python gebruik ik om bestanden in te lezen, data te verwerken, verbinding te maken met databases en de LLM aan te roepen.

Voor de LLM gebruik ik bijvoorbeeld de Openrouter API. Deze gebruik ik om analyses, definities en rapporten te genereren.

MongoDB gebruik ik om de originele informatie op te slaan, zoals HUMINT-bestanden, WEBINT-resultaten, LLM-antwoorden en rapporten.

Qdrant gebruik ik als vector database. Hierin sla ik embeddings op, zodat het systeem informatie op betekenis kan terugvinden.

Docker gebruik ik om MongoDB en Qdrant lokaal te draaien zonder dat ik alles handmatig hoef te installeren.  

Daarnaast gebruik ik markdownbestanden voor prompts en HUMINT-data.



## Hoe ik de onderdelen ga implementeren

De HUMINT-data wordt opgeslagen in een aparte map met markdownbestanden. Het systeem leest alle bestanden uit deze map in en slaat de inhoud op in MongoDB.

De WEBINT-data wordt verzameld via online bronnen of, voor deze opdracht, gesimuleerd met fictieve webinformatie zoals vacatureteksten. Ook deze informatie wordt opgeslagen in MongoDB.

Daarna wordt alle tekst opgesplitst in kleinere chunks. Van elke chunk wordt een embedding gemaakt. Deze embeddings worden opgeslagen in Qdrant, samen met metadata zoals klantnaam, bron en documenttype.

De prompts worden opgeslagen in een aparte prompt-directory. De bestandsnamen krijgen een nummer, bijvoorbeeld 001-algemene-info.md en 002-verdieping.md. Het systeem leest deze prompts automatisch in volgorde in. Daardoor kunnen later nieuwe prompts worden toegevoegd zonder dat de code aangepast hoeft te worden.

Wanneer het systeem een analyse uitvoert, zoekt het eerst relevante informatie op in Qdrant. Deze informatie wordt samen met de prompt naar de LLM gestuurd. De LLM schrijft vervolgens een antwoord.

Uit dat antwoord worden technische termen gehaald. Voor elke term controleert het systeem of er al een definitie of uitleg beschikbaar is. Als dat niet zo is, wordt een vervolgprompt naar de LLM gestuurd. De nieuwe uitleg wordt daarna opgeslagen in MongoDB en Qdrant.

Aan het einde worden alle verzamelde gegevens gebruikt om een markdownrapport te maken over het technische landschap van de klant.

## Hoe ik de prestaties ga evalueren

Ik ga het systeem evalueren door te controleren of de informatie logisch, bruikbaar en herleidbaar is.

Ik kijk of het systeem relevante HUMINT- en WEBINT-informatie terugvindt. Ook controleer ik of de LLM-antwoorden gebaseerd zijn op de opgehaalde context en niet zomaar informatie verzinnen.

Daarnaast test ik of technische termen goed worden herkend en of definities niet dubbel worden opgeslagen. Ik controleer ook of het iteratieve promptingproces werkt: het systeem moet na een eerste analyse vervolgvragen kunnen stellen over gevonden technologieën.

Verder beoordeel ik het eindrapport op volledigheid, duidelijkheid en structuur. Het rapport moet uitleggen welke technologieën de klant gebruikt, welke bronnen daarvoor zijn gebruikt en welke conclusies daaruit worden getrokken.

Voorbeeldvragen waarmee ik kan testen zijn:

Welke technologieën gebruikt Klant X?
Welke cloudplatformen komen terug in de bronnen?
Welke programmeertalen worden genoemd?
Worden technische termen correct uitgelegd?
Gebruikt het systeem bestaande definities opnieuw?

Zo kan ik bepalen of het systeem technisch werkt en inhoudelijk bruikbare resultaten oplevert.




### Technische Ontwerp 

1. Lees configuratiebestand
2. Lees HUMINT markdownfiles
3. Lees WEBINT markdownfiles
4. Sla documenten op in MongoDB
5. Split tekst in chunks
6. Maak embeddings
7. Sla embeddings op in Qdrant
8. Lees prompts uit prompt-directory
9. Voer prompts uit in numerieke volgorde
10. Zoek relevante context in Qdrant
11. Stuur prompt + context naar LLM
12. Sla LLM-output op in MongoDB
13. Extraheer technische termen
14. Controleer of termen al bekend zijn
15. Genereer vervolgprompts voor onbekende termen
16. Sla nieuwe kennis op
17. Genereer eindrapport

```shell
CIRQUI System
│
├── INSTRUCTION READER
│   └── Leest WEBINT-instructies
│
├── PROMPT ARGUMENT LOADER
│   └── Leest configuratie- en promptargumenten
│
├── WEBINT COLLECTOR
│   └── Verzamelt publieke WEBINT via Codex
│
├── MARKDOWN WRITER
│   └── Genereert WEBINT- en rapportbestanden in markdown
│
├── INTELLIGENCE READER
│   ├── Leest HUMINT-bestanden
│   └── Leest WEBINT-bestanden
│
├── MONGODB REPOSITORY
│   └── Opslag van documenten, analyses en rapporten
│
├── CHUNKING SERVICE
│   └── Splitst tekst op in chunks
│
├── EMBEDDING SERVICE
│   └── Genereert embeddings via embedding API
│
├── QDRANT REPOSITORY
│   └── Opslag van embeddings in Qdrant
│
├── PROMPT READER
│   └── Leest prompts uit prompt-directory
│
├── CONTEXT RETRIEVER
│   └── Haalt relevante context op via semantic search
│
├── LLM CLIENT
│   └── Communicatie met OpenAI API
│
├── TECHNICAL TERM EXTRACTOR
│   └── Extraheert technische termen via LLM-prompts
│
├── KNOWLEDGE CHECKER
│   └── Controleert of kennis bestaat in Qdrant
│
├── WORKFLOW ORCHESTRATOR
│   ├── Start iteratieve analyses
│   ├── Genereert vervolgprompts
│   └── Stuurt workflow aan
│
├── REPORT GENERATOR
│   └── Genereert markdown eindrapport
│
└── REPORT WRITER
    └── Slaat rapporten op als markdownbestand
```


### Huidige implementatie
De huidige versie van het systeem kan:

- configuratiebestanden inlezen
- HUMINT-markdownbestanden verwerken
- prompts laden vanuit een prompt-directory
- prompts naar een LLM sturen
- technische termen extraheren
- termen vergelijken met bestaande MongoDB-data
- embeddings genereren
- embeddings opslaan in Qdrant

``` shell


Huidige CIRQUI Systeem
│
├── CONFIG READER
│   └── Leest configuratie-instellingen uit config.txt
│
├── PROMPT READER
│   └── Leest prompt templates uit de prompt-directory
│
├── HUMINT READER
│   └── Leest HUMINT-markdownbestanden van klanten
│
├── LLM CLIENT
│   └── Stuurt prompts naar het LLM en ontvangt antwoorden
│
├── TECHNICAL TERM EXTRACTOR
│   └── Extraheert technische termen uit LLM-output
│
├── TERM COMPARATOR
│   └── Controleert of technische termen al bestaan in MongoDB
│
├── MONGODB REPOSITORY
│   └── Opslag van technische termen en analyses
│
├── EMBEDDING SERVICE
│   └── Genereert embeddings van termen via embedding API
│
├── QDRANT REPOSITORY
│   └── Opslag van embeddings in Qdrant
│
└── MAIN WORKFLOW
    └── Stuurt de volledige analysepipeline aan
```

## Wat momenteel nog ontbreekt

De huidige versie van het systeem bevat al een eerste werkende pipeline, maar een aantal onderdelen uit het ontwerp zijn nog niet volledig geïmplementeerd.

* WEBINT wordt momenteel nog niet automatisch verzameld via publieke websites. Dit wil ik later toevoegen via een aparte WEBINT-module.
* Het iteratieve promptingmechanisme is nog niet volledig uitgewerkt. In een volgende versie wil ik automatisch vervolgprompts genereren op basis van gevonden technische termen.
* Qdrant wordt momenteel gebruikt voor opslag van embeddings, maar semantic search wordt nog niet actief gebruikt tijdens analyses.
* Chunking van documenten is nog niet geïmplementeerd. Later wil ik teksten automatisch opdelen in kleinere stukken voor betere embeddings.
* Het systeem genereert momenteel nog geen volledig automatisch markdownrapport.
* De workflowlogica staat nu grotendeels in `main.py`. In een volgende versie wil ik dit opsplitsen in aparte workflowcomponenten.
* Momenteel wordt één prompt handmatig geladen. Later wil ik meerdere prompts automatisch in numerieke volgorde laten uitvoeren.
