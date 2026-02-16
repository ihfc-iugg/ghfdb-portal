# Phase 1 Project

## WP1: Requirement Analysis, Data Management & Collaborative Enrichment

**Lead:** GFZ (Sven Fuchs)  
**Involved:** TUD, collaborative network  
**Timeline:** M1–M36  
**Personnel:**

- Postdoc (100%, 36 PM) - Work in WP1 and WP4
- Student Worker (40h/month, 36 months) - Data screening, literature review and assessment

### Objectives

To optimize and update the present database towards the new structure and quality requirements.

### Description

Based on community needs and international best practice recommendations (from Global Collaborative Data Assessment), a new database model will be developed considering the data and metadata.

#### Metadata Schema Development

- Metadata for data discovery and contextual metadata
- Based on international standards
- Include geo-location fields and persistent identifiers (with WP2):
  - Literature references (DOI)
  - Author identification (ORCID)
  - Institute identifier (ROR)
  - Sample identifier (IGSN)
  - Methodological catalogues
- Linked-open data enable search facets

#### Data Classification & Quality

- Use first project workshop to develop and finalize new schemes of data classification and quality
- Categories for faceted search and selection in graphical user interface (WP3)
- Extended and newly structured data compilation enriched with:
  - Quality-relevant information (methods used, corrections applied)
  - Screen primary and secondary literature for each data entry
  - Add flags on data quality and status
  - Add additional selector variables

#### Collaborative Data Assessment

- 66 researchers committed to support data revision
- Formal Task Force of International Lithosphere Program (ILP)
- IHFC members and ILP-TF leaders form advisory board and core team
- Evaluation starts with pre-analyzed heat-flow data of Germany and surrounding countries
- Well-documented frequent releases (starting with annual frequency) for download
- Share in international trusted data repositories

### Deliverables

- **D1.1** - New database structure (M3)
- **D1.2** - New heat-flow quality classification scheme (M9)
- **D1.3** - 50% of initial global dataset updated (M30)

### Tasks

- Task 1.1 - Inventory of present database and definition of data storage demand (GFZ)
- Task 1.2 - Analysis of community expectations and requirements (GFZ)
- Task 1.3 - Develop database model and metadata schema (GFZ & TUD)
- Task 1.4 - Implementation of international collaborative community approach (GFZ)
- Task 1.5 - Development of quality classes and data classification (GFZ + collaborative network)
- Task 1.6 - Data transfer and metadata enrichment, including setup of reference and author sub-database with persistent identifiers (GFZ + collaborative network)
- Task 1.7 - Update and extension of historical data (GFZ + collaborative network)

### Cross-Package Dependencies

#### WP1 → WP2 (Backend)

- WP1 defines database model for WP2 implementation
- WP1 metadata schema informs WP2 architecture

#### WP1 → WP3 (Frontend)

- WP1 quality classes and data classification used for faceted search in WP3
- WP1 selector variables displayed in WP3 GUI

---

## WP2: Data Portal Backend, Architecture & Interoperability

**Lead:** GFZ (Kirsten Elger)  
**Involved:** TUD  
**Timeline:** M1–M36  
**Personnel:**

- Scientific Associate (100%, 36 PM) - Lead and work in WP3, support WP2
- Student Worker (40h/month, 36 months) - Literature review, tools & website programming

### Objectives

1. Develop the technical backbone of a web-based data portal
2. Implement DOI-minting service
3. Enable interoperability to other geoscientific data services

### Description

Based on community needs, the new database model (WP1) will be implemented and the architecture of the research data infrastructure will be conceptualized and designed.

#### Architecture & Database Technology

- Decision at project start: SQL-based (relational PostgreSQL) or noSQL-based (graph-based)
- Both technologies provide open source solutions meeting project requirements
- Leverage in-house GFZ experiences:
  - SQL: Similar to World Stress Map with DOI-minting service
  - noSQL: Similar to Varved Sediment Database

#### Core Infrastructure Components

WP2 focuses on the technical backbone of functions developed in WP3:

- Web-based data portal
- Project webpage
- Community areas
- Data submission system
- Interconnected literature and author database
- Graphical user interface to the database

#### DOI Minting Service

- For user-submitted data with adequate metadata description
- Direct link to GFZ Data Services via standardized API
- Initiates data publication workflow with DOI
- Novelty for heat-flow data - major incentive for community
- Metadata capture supported by online metadata editor
- Similar to GFZ Metadata Editor
- Follows international standards (ISO19115, DataCite, OGC)
- Converts to machine-readable metadata (JSON, XML formats)

#### Authorization & Review System

- Authorization and authentication system
- Different access levels (administrator, super user, reviewer, user)
- Internal review area for newly submitted and revised data
- Changes tracked and publicly documented with each release

#### Persistent Identifiers Integration

Each heat-flow data connected to:

- Original literature reference (heat flow literature database)
- DOI number (where available)
- IGSNs of originating samples (where available)
- Authors' ORCID and/or ResearcherID
- Facilitates connection to ORCID records via DOI-referenced data publications
- Petrophysical data connected to sample's IGSN
- References, identifiers and researchers as selector variables in GUI (WP3)

### Deliverables

- **D2.1** - Database (M12+)
- **D2.2** - Submission system with technical validity check (M18)
- **D2.3** - Revision and user rights system (M18)
- **D2.4** - Commentary and annotation system of heat flow data (M24)
- **D2.5** - Download and data science UI (M32)
- **D2.6** - Data portal with implemented visualization modules from WP3 (M34)

### Tasks

- Task 2.1 - Allocation of physical storage and server capacity (GFZ)
- Task 2.2 - Develop interaction strategy for front-end-back-end communication structure and interfacing (GFZ & TUD)
- Task 2.3 - Development and programming of database, incl. user authentication system (GFZ)
- Task 2.4 - Development of API for metadata exchange (e.g., data publications via GFZ Data Services, author identification via ORCID, interoperability with IGSN metadata) (GFZ)
- Task 2.5 - Conceptual workflow design of data submission system, user interface and backend communication structure (GFZ)
- Task 2.6 - Setup of web-based data portal and programming of web interface for data and metadata submission process (incl. server-side validity check) and feedback form (GFZ)
- Task 2.7 - Conceptual design and programming data download interface in various file formats or full database dump (GFZ & TUD)

### Cross-Package Dependencies

#### WP1 → WP2 (Data Management)

- WP1 database model implemented in WP2
- WP1 metadata schema (ISO19115, DataCite, OGC) guides WP2 metadata editor

#### WP2 → WP3 (Frontend)

- WP2 provides technical backbone for WP3 functions
- WP2 selector variables (references, identifiers, researchers) displayed in WP3 GUI
- WP2 submission system validated by WP3
- WP2 DOI service basis for WP3 validation

---

## WP3: Data Portal Frontend, Exploration, Visualization & Mapping

**Lead:** TUD (Stephan Mäs)  
**Involved:** GFZ  
**Timeline:** M1–M36  
**Personnel:**

- Scientific Associate (100%, 36 PM) - Lead and work of WP2, support WP3
- Student Worker (40h/month, 36 months) - Literature review, tool programming and usability evaluation

### Objectives

1. Develop web-based front-end for data portal
2. Integrated data selection criteria and search functions
3. Visualizations supporting data exploration
4. Statistical analysis and interpolation functionalities

### Description

A web-based data portal will be set up offering comprehensive user-facing features and analytical tools.

#### Search & Selection Functions

- Integrated search function with:
  - Faceted search based on defined categories
  - Keyword-based search
  - Search by relevant criteria (type of heat flow, quality criteria, errors)
  - Spatio-temporal extent search
  - Authors and years search

#### Mapping & Visualization Tools

Developed in several implementation steps to support spatial and/or statistical analysis:

- Spatial interpolations (spherical harmonic analysis)
- Descriptive statistical visualizations with uncertainties
- Digital boreholes visualization (1D thermal profiles)
- Spatial crustal profiles (2D thermal cross-sections, e.g., from mid-oceanic ridge)

#### Data Submission System

Two submission methods:

1. **Manual submission:** via input form
2. **Automatic submission:** via data file upload
   - Predefined structure for CSV, JSON, or XML file
   - Excel file with predefined table structure and restricted input options
   - Automatic validation for logical consistency, completeness, and accuracy
   - Integrated validation enables DOI service (WP2)
   - Failed validation generates report for data provider revision

#### Data Download & Export

- Standardized interfaces (e.g., WMS for map visualizations)
- Common formats: CSV, GeoJSON, GeoTIFF, netCDF
- Metadata export conform to ISO 19115 and 19139
- Formats discussed with user communities

#### Community Features

- Feedback form for commentaries and annotations on existing data
- Collect observations and experiences from worldwide researchers
- FAQ and help section with structured contents (decision tree)
- Interactive assistance for users
- Helpdesk contact information

#### Usability & User Experience

- Regular usability evaluations
- User studies to ensure portal meets requirements
- Implementation process supported by user feedback
- Maximize usability and benefit for geoscientists
- Minimize effort during data ingest

### Deliverables

- **D3.1** - Basic portal and frontend (M12)
- **D3.2** - Search functions implemented (M18)
- **D3.3** - Visualization system (2D point data) with database (M24)
- **D3.4** - Data interpolation functionalities implemented and integrated (M30)
- **D3.5** - Statistical analysis and data exploration implemented and integrated (M36)

### Tasks

- Task 3.1 - Conceptual design of user interface, user interactions, visualization, analysis and interpolation functions and backend communication structure (TUD)
- Task 3.2 - Development and implementation of basic web framework and data portal integrating all functions (TUD)
- Task 3.3 - Keyword-based and area-based search and selection functions in GUI (GFZ & TUD)
- Task 3.4 - Basic 2D visualization of point data sets based on user selection criteria (TUD)
- Task 3.5 - Implementation of regionalized interpolation algorithms (TUD)
- Task 3.6 - Statistical analysis and chart visualization of selected data, spatial areas or cross sections (TUD)
- Task 3.7 - Data exploration visualizations (digital boreholes and cross sections) (TUD)
- Task 3.8 - Community feedback and usability evaluation (GFZ & TUD)

### Cross-Package Dependencies

#### WP1 → WP3 (Data & Quality)

- WP1 quality classes used for faceted search and selection in WP3
- WP1 selector variables displayed in WP3 GUI

#### WP2 → WP3 (Backend Support)

- WP3 functions built on WP2 technical backbone
- WP3 submission validation basis for WP2 DOI service
- WP3 visualization modules implemented in WP2 data portal (D2.6)

---

## WP4: Community, Dissemination, Outreach & Project Management

**Lead:** GFZ (Sven Fuchs)  
**Involved:** TUD  
**Timeline:** M1–M36

### Objectives

1. Coordination, execution and follow-up of scientific program (WP1-3)
2. Recruitment and management of timetable and financial resources
3. Coordinating and implementing collaborative work of international community
4. Coordinating communications
5. Ensuring widest dissemination and outreach events
6. Adequate exploitation of project results

### Deliverables

- **D4.1** - Consortium agreement (M1)
- **D4.2** - Recruitment finished (M1)
- **D4.3** - Website and project wiki online (M3)
- **D4.4** - Project newsletter implemented and brochure developed and printed (M6+)
- **D4.5-4.8** - Workshops organized and held (M9-36)
- **D4.9** - Scientific conferences attended (M12+)
- **D4.10** - Periodic and final reports (M18-36)

### Tasks

- Task 4.1 - Coordination of consortium agreement (GFZ)
- Task 4.2 - Recruitment (GFZ & TUD)
- Task 4.3 - Implementation of collaborative community approach; organization of continental workshops (GFZ)
- Task 4.4 - Dissemination of scientific results (GFZ & TUD)
- Task 4.5 - Communication and public engagement (GFZ)
- Task 4.6 - Monitoring and controlling of project progress (GFZ)
- Task 4.7 - Coordination of meetings & reports (GFZ & TUD)

**Note:** WP4 is primarily organizational and does not directly involve portal codebase development.
