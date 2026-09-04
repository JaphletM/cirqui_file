**Technisch Landschap Rapport: Van Geloven**

**Datum:** 26 mei 2024
**Auteur:** Technische Analist
**Betrouwbaarheid Informatie:** Gemiddeld - Gebaseerd op algemene kennis van de FMCG-sector, externe analyses en de verstrekte (zij het beperkte) informatie over specifieke tools. Directe inzage in de bedrijfs systemen is niet beschikbaar.

---

**1. Samenvatting**

Dit rapport beoogt een technisch landschap van Van Geloven te schetsen, gebaseerd op de verstrekte informatie en algemene industriestandaarden binnen de Fast Moving Consumer Goods (FMCG) sector, in het bijzonder de voedselproductie. Gezien de aard van Van Geloven als een grootschalige voedselproducent, ligt de focus op systemen die essentieel zijn voor productie, logistiek, bedrijfsvoering en algemene IT-infrastructuur.

Het technische landschap van Van Geloven kenmerkt zich, zoals gebruikelijk bij bedrijven van deze omvang, door een combinatie van operationele technologie (OT) op de productielijnen en informatietechnologie (IT) voor bedrijfsprocessen. De vermelde tools zoals SAP, Microsoft 365, en Office 365 bevestigen dit IT-aspect.

**2. Geïdentificeerde Kerncomponenten van het Technisch Landschap**

Gebaseerd op de algemene industrie context en de vermelde tools, kunnen we de volgende kerncomponenten van het technische landschap van Van Geloven identificeren:

**2.1. Enterprise Resource Planning (ERP)**
*   **SAP:** Als een van de meest vooraanstaande ERP-systemen in de wereld, is SAP cruciaal voor het integreren en beheren van alle kernprocessen binnen Van Geloven. Dit omvat waarschijnlijk:
    *   **Productieplanning en -controle:** Beheer van grondstoffen, recepturen, processen en planning van productielijnen.
    *   **Logistiek en Supply Chain Management (SCM):** Inkoop, voorraadbeheer van grondstoffen en eindproducten, distributie en transportplanning.
    *   **Financiën en Controlling:** Boekhouding, budgettering, kostenbeheer en rapportage.
    *   **Human Capital Management (HCM):** Personeelsadministratie, salarisverwerking (indien geïntegreerd).
    *   **Verkoop en Distributie (SD):** Orderbeheer, facturering en klantrelatiebeheer op een basaal niveau.

**2.2. Productiviteit, Samenwerking en Cloud Services**
*   **Microsoft 365 (inclusief Office 365):** Dit pakket is essentieel voor de dagelijkse kantoorproductiviteit en samenwerking. De diepere analyse onthult het volgende:
    *   **Kernapplicaties (Word, Excel, PowerPoint, Outlook):** Intensief gebruikt voor documentcreatie, data-analyse, presentaties en communicatie. Desktopversies zijn dominant, web-based voor flexibiliteit.
    *   **Samenwerkingsplatformen (Teams, SharePoint, OneDrive):** Cruciaal voor interne communicatie, projectmanagement, documentbeheer en gecentraliseerde opslag. Co-auteurschap en bestand delen zijn standaard geworden.
    *   **Cloud Infrastructuur:** Exchange Online voor e-mail, SharePoint voor intranetten en documentopslag, OneDrive voor persoonlijke opslag. Dit duidt op een aanzienlijke afhankelijkheid van Microsoft's cloud-diensten.
    *   **Licentiestructuur:** Een mix van Business Standard, Business Premium en Business Basic, afgestemd op verschillende rollen (kantoor, IT/Directie, verkoop). Er is een trend naar uitbreiding van Premium en overweging van E3 voor gespecialiseerde rollen.
    *   **Beveiliging & Compliance:** Actief beleid met MFA, Conditional Access, en DLP. Sterke focus op AVG-compliance. Zorgen over data residency bij internationale projecten en sector-specifieke eisen voor Finance.

**2.3. Operationele Technologie (OT) en Productieautomatisering (Inferred/Aannames)**
Hoewel niet specifiek genoemd, is dit een cruciale component voor een voedselproducent als Van Geloven:
*   **SCADA (Supervisory Control and Data Acquisition)/MES (Manufacturing Execution System):** Essentieel voor het monitoren en aansturen van machines en processen op de productielijnen. MES integreert met ERP (SAP) om productieorders te vertalen naar werkvloeractiviteiten en real-time data terug te koppelen.
*   **PLC's (Programmable Logic Controllers):** Voor de automatisering en besturing van individuele machines en processen (bijv. mengen, bakken, verpakken, koeling).
*   **Robotica & Automatisering:** Voor efficiëntie, consistentie en arbeidsbesparing in taken zoals handling, assemblage en verpakking. Dit draagt bij aan "beter, efficiënter" produceren.
*   **Sensoren en IoT (Internet of Things):** Voor het verzamelen van real-time data over temperatuur, vochtigheid, drukken, machineprestaties etc., cruciaal voor kwaliteitscontrole, efficiëntie en predictive maintenance.
*   **Kwaliteitscontrolesystemen:** Geïntegreerd in de productielijnen om productconformiteit te waarborgen (haccp-monitoring).

**2.4. Data-analyse en Business Intelligence (Inferred)**
*   **Data Warehousing/Databases:** Om grote hoeveelheden operationele en transactionele data op te slaan.
*   **BI-Tools:** Zoals Microsoft Power BI (vaak complementair aan Microsoft 365), Tableau of QlikView voor het analyseren van prestaties, efficiëntie, verkoopcijfers en trends. Dit ondersteunt het maken van data-gedreven beslissingen.
*   **Advanced Analytics/AI:** Mogelijk in een exploratieve fase voor optimalisatie van recepturen, voorspelling van vraag, of preventief onderhoud.

**2.5. Netwerk & Infrastructuur (Inferred)**
*   **Lokale Netwerken (LAN/WLAN):** Betrouwbare connectiviteit voor kantooromgevingen en productielijnen.
*   **Wide Area Networks (WAN):** Voor communicatie tussen verschillende productielocaties, distributiecentra en kantoren.
*   **Cybersecurity-infrastructuur:** Firewalls, Intrusion Detection/Prevention Systems (IDS/IPS), Endpoint Detection & Response (EDR) als aanvulling op Microsoft 365's beveiliging.

---

**3. Tools en Skills gezocht binnen Van Geloven**

Op basis van het geschetste technische landschap en de specifieke behoeften die zijn gedetailleerd in de analyse van Microsoft 365, kunnen de volgende tools en vaardigheden worden geïdentificeerd als cruciaal voor Van Geloven:

**3.1. Tools**

*   **SAP ECC/S/4HANA:** Diepgaande kennis van modules relevant voor FMCG (PP, MM, SD, FICO), inclusief configuratie en beheer. Migratie-ervaring naar S/4HANA is een plus.
*   **Microsoft 365 Suite:**
    *   **End-user proficientie:** Word, Excel, PowerPoint, Outlook.
    *   **Administrator/Expertise:** Teams (governance, kanalen, apps), SharePoint Online (sites, documentbeheer, workflows), OneDrive (synchronisatie), Exchange Online (beheer), Power Platform (Power Apps, Power Automate, Power BI).
    *   **Beveiligingstools:** Ervaring met Azure Active Directory (Conditional Access, MFA), DLP, Intune (device management), Defender (voor Endpoint/Identity).
*   **SCADA/MES-systemen:** Ervaring met platforms zoals Siemens TIA Portal, Rockwell Automation FactoryTalk, of specifieke brancheoplossingen. Kennis van ISA-95 model is relevant.
*   **PLC-programmering:** Kennis van gangbare PLC-platformen (Siemens S7, Allen-Bradley, Omron) en programmeertalen (Ladder Logic, Function Block Diagram).
*   **Data Analytics & BI Tools:** Power BI (zeer waarschijnlijk), Tableau, Qlik of vergelijkbare tools, inclusief kennis van SQL voor data-extractie.
*   **Cloud Platforms:** Basis begrip van Azure-services, gezien de M365-basis, voor mogelijke uitbreiding van infrastructurele diensten.
*   **IT Service Management (ITSM) Tools:** Zoals ServiceNow, Jira Service Management voor incident-, probleem- en change management.

**3.2. Skills (Technisch & Soft Skills)**

*   **SAP Consultants/Specialisten:** Voor functionele en technische ondersteuning en optimalisatie van de ERP-omgeving.
*   **Microsoft 365 Experts:** Voor advies, implementatie en beheer van de M365-omgeving, inclusief licenties, beveiliging en compliance.
*   **Systeembeheerders (Azure AD, M365):** Voor het beheer van gebruikers, groepen, beleid en beveiliging binnen de Microsoft cloudomgeving.
*   **Productie IT/OT Engineers:** Met expertise in SCADA/MES-systemen, PLC-programmering, robotica en industriële netwerken. Deze specialisten overbruggen de kloof tussen IT en productie.
*   **Data Analisten/Wetenschappers:** Voor het extraheren, transformeren, laden (ETL) en analyseren van data ter ondersteuning van business decision-making.
*   **Netwerk Engineers:** Voor het ontwerpen, implementeren en onderhouden van robuuste en veilige netwerkinfrastructuren.
*   **Cybersecurity Specialisten:** Voor het proactief identificeren, mitigeren en reageren op beveiligingsrisico's.
*   **Project Managers:** Met ervaring in IT- en OT-implementaties, bij voorkeur in de FMCG-sector.
*   **Change Management Specialists:** Zeer relevant, gezien de behoefte aan training en adoptie van nieuwe functionaliteiten binnen M365 en andere systemen.
*   **Problem-Solving & Analytische Vaardigheden:** Cruciaal voor het diagnosticeren en oplossen van complexe technische problemen.
*   **Communicatievaardigheden:** Essentieel voor het samenwerken met verschillende afdelingen (productie, sales, finance) en het vertalen van technische concepten naar businessbehoeften.
*   **Kennis van FMCG/Voedselproductie Processen:** Een diepgaand begrip van de specifieke eisen en uitdagingen in de voedselindustrie (bv. HACCP, voedselveiligheid, tracking & tracing, korte houdbaarheidsdata).

---

**4. Aanbevelingen**
Om het technische landschap verder te verdiepen en de efficiency van Van Geloven te verhogen, wordt aanbevolen om te focussen op:
*   **Optimalisatie van Power Platform:** Investering in training en specialistische ondersteuning om Power Apps en Power Automate beter te benutten voor procesautomatisering.
*   **Versterking van Cybersecurity:** Met name op het gebied van OT-beveiliging en gedetailleerde compliance-afspraken voor data residency bij internationale projecten.
*   **Integratie van IT en OT:** Verdere harmonisatie en datatransparantie tussen ERP, MES en PLC-lagen om real-time zichtbaarheid en controle over de gehele waardeketen te verbeteren.
*   **Gestructureerde Communicatie en Training:** Voor updates en nieuwe functionaliteiten binnen Microsoft 365 om verstoringen te minimaliseren en adoptie te maximaliseren.

Dit rapport biedt een solide basis voor het begrijpen van de technische omgeving van Van Geloven en de bijbehorende competentiebehoeften.