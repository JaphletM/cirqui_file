## Wat de opdracht inhoudt

In deze opdracht bouw ik een systeem dat het technische landschap van een klant onderzoekt. Het systeem verzamelt informatie uit HUMINT en WEBINT. HUMINT bestaat uit menselijke bronnen, zoals gesprekken, interviews of notities. WEBINT bestaat uit publiek beschikbare online informatie, zoals websites, vacatures en documentatie.

Het doel is om met behulp van een LLM een rapport te maken over welke technologieën, tools, platformen en systemen een klant waarschijnlijk gebruikt. Het systeem haalt ook technische termen uit de antwoorden van de LLM. Als het systeem een term nog niet kent, wordt daar extra informatie over opgezocht en opgeslagen voor later gebruik.

## Welke stappen ik ga ondernemen
1. Ik maak fictieve HUMINT-bestanden aan in markdown.
Ik maak of verzamel WEBINT-informatie, bijvoorbeeld uit fictieve vacatures of websites.
Ik lees deze bestanden in met Python.
Ik sla de ruwe informatie op in MongoDB.
Ik splits de tekst op in kleinere stukken.
Ik zet deze stukken om naar embeddings.
Ik sla deze embeddings op in Qdrant.
Ik lees vaste prompts in uit een prompt-directory.
Ik stuur de prompt met relevante context naar de LLM.
Ik laat de LLM een eerste analyse maken van het technische landschap.
Ik haal technische termen uit het antwoord.
Ik controleer of deze termen al bekend zijn in de vector store.
Als een term nog niet bekend is, vraag ik extra uitleg aan de LLM.
Ik sla deze nieuwe informatie op in MongoDB en Qdrant.
Ik herhaal dit proces voor vervolgprompts.
Tot slot laat ik het systeem een markdownrapport genereren.

## Welke tools en technologieën ik ga gebruiken

Ik ga Python gebruiken als programmeertaal. Python gebruik ik om bestanden in te lezen, data te verwerken, verbinding te maken met databases en de LLM aan te roepen.

Voor de LLM gebruik ik bijvoorbeeld de OpenAI API. Deze gebruik ik om analyses, definities en rapporten te genereren.

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




### Opdracht 2 
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


CIRQUI System
│
├── ConfigLoader
│   └── Leest configuratiebestanden
│
├── FileIngestionModule
│   ├── Leest HUMINT bestanden
│   └── Leest WEBINT bestanden
│
├── MongoRepository
│   └── Opslag van documenten en analyses
│
├── TextChunker
│   └── Splitst tekst op in chunks
│
├── EmbeddingService
│   └── Genereert embeddings
│
├── QdrantRepository
│   ├── Opslag van embeddings
│   └── Semantic search
│
├── PromptLoader
│   └── Leest prompts uit directory
│
├── LLMService
│   └── Communicatie met OpenAI API
│
├── TermExtractor
│   └── Herkent technische termen
│
├── IterationManager
│   ├── Controleert bestaande kennis
│   ├── Genereert vervolgprompts
│   └── Start nieuwe analyses
│
└── ReportGenerator
    └── Genereert eindrapport



De FileIngestionModule leest HUMINT- en WEBINT-bestanden in en stuurt deze door naar MongoRepository.

De TextChunker splitst documenten op in kleinere stukken tekst. Daarna maakt de EmbeddingService embeddings van deze chunks.

Deze embeddings worden opgeslagen in QdrantRepository.

De PromptLoader leest prompts uit de prompt-directory. Vervolgens haalt QdrantRepository relevante context op.

De LLMService stuurt prompts en context naar de OpenAI API.

De antwoorden worden opgeslagen in MongoDB. Daarna gebruikt TermExtractor de output om technische termen te herkennen.

De IterationManager controleert of kennis over deze termen al bestaat. Als dat niet zo is, worden vervolgprompts gegenereerd.

Tot slot maakt ReportGenerator een eindrapport.