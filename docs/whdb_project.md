# The World Heat Flow Database Project

## Overview

The World Heat Flow Database (WHDB) Project represents a comprehensive initiative to develop a modern research data infrastructure for global terrestrial heat-flow data, enabling the geoscientific community to efficiently access the results of over a century of global heat-flow research and data collection.

The project is funded by the Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) under grant number 491795283 and is executed in two phases, with development and implementation led by a collaboration between GFZ German Research Centre for Geosciences, Technical University of Dresden (TU Dresden), and the University of Bremen/MARUM.

## Project Mission

The WHDB Project aims to provide a national and international contribution to heat-flow research by developing a new heat-flow research data infrastructure that enables extended interpretations based on modern data analysis and visualization tools. The infrastructure serves as a **one-stop shop** for heat-flow information and data, offering quality-assessed, up-to-date, well-documented, and restructured heat-flow data with comprehensive discovery, visualization, download, and data publication capabilities.

## Project Phases

### Phase One: Database Development (2022-2025)

The first phase focused on building the foundational research data infrastructure and web portal at [portal.heatflow.world](https://portal.heatflow.world). Key accomplishments included:

- Development of a new database structure reflecting modern metadata standards
- Implementation of a quality evaluation scheme for heat-flow data
- Creation of a user-oriented web service providing access to quality-proofed data
- Initial global data assessment and collaborative data revision
- Integration of persistent identifiers (DOI, ORCID, IGSN)
- Launch of the public portal in July 2025

**Primary Partners**:
- **GFZ German Research Centre for Geosciences**: Project leadership, database development, data curation (Principal Investigators: Dr. Sven Fuchs, Dr. Kirsten Elger, Dr. Ben Norden)
- **Technical University of Dresden**: Web-based infrastructure development, geoinformatics, visualization tools (Principal Investigator: Prof. Dr.-Ing. Stephan Mäs)

### Phase Two: Portal Enhancement (2025-2028)

The second phase, currently underway, focuses on consolidating and expanding the research data infrastructure with emphasis on:

- Completing the global data assessment
- Transitioning data publication to a fully semi-automated system
- Expanding database coverage with new data types (especially marine heat-flow data)
- Strengthening front-end and back-end functionalities
- Adding advanced API representations and analytical tools
- Developing educational resources and community-driven enrichment features
- Bridging geoscience and oceanography through integration of marine heat-flow data

**Extended Partnership**:
- **University of Bremen/MARUM**: Marine heat-flow data integration (Principal Investigator: Prof. Dr. Achim Kopf)

## Research Data Infrastructure

### Core Technical Components

The WHDB portal infrastructure is built on modern, sustainable architectural principles designed for long-term operation and interoperability with the broader geoscientific research ecosystem.

#### Database Architecture

The research data infrastructure employs a relational database architecture (PostgreSQL) that supports:

- **Structured metadata storage** following international standards (ISO 19115, DataCite, OGC)
- **Machine-readable data exchange** in multiple formats (JSON, XML, CSV, GeoJSON, netCDF)
- **Quality-controlled data ingestion** with automated validation and review workflows
- **Version control and change tracking** for all data releases
- **User authentication and authorization** system with role-based access control

#### Data Publication Service

A critical innovation of the WHDB infrastructure is the integrated DOI minting service developed in collaboration with **GFZ Data Services**. This service enables:

- **Direct data publication** through a standardized API connecting to GFZ Data Services
- **Citable research products**: DOI-referenced heat-flow datasets as fully citable publications
- **Researcher attribution**: Automatic linking to ORCID identifiers for proper academic credit
- **Sample connectivity**: Integration with International Geo Sample Numbers (IGSN) for physical samples
- **Literature linkage**: Connection to original research publications via DOI references

GFZ Data Services has been a pioneer in research data management since assigning its first DOI in 2004 and serves as an international research data repository for the Geosciences domain. The WHDB project benefits from GFZ's extensive experience developing DOI minting services for major international projects and networks, including the International Association for Geodesy services (ICGEM, IGETS, ISG), World Stress Map, INTERMAGNET, and numerous others.

#### Persistent Identifier Integration

The infrastructure systematically incorporates globally recognized persistent identifiers:

- **DOI (Digital Object Identifier)**: For datasets, enabling permanent citation and data publication
- **ORCID (Open Researcher and Contributor ID)**: For author identification and research attribution
- **IGSN (International Geo Sample Number)**: For connecting data to physical rock samples
- **ROR (Research Organization Registry)**: For institutional affiliation tracking

This interconnected identifier system creates a rich, linked-open-data ecosystem that supports reproducible science and proper attribution throughout the research lifecycle.

### Metadata Standards and Quality Framework

#### Metadata Schema

The WHDB metadata model was developed through extensive international collaboration with heat-flow experts and reflects community requirements for scientific reproducibility. The schema includes:

- **Discovery metadata**: Geographic location, temporal coverage, authorship, keywords
- **Contextual metadata**: Methodological details, corrections applied, quality indicators, geological setting
- **Provenance metadata**: Data lineage, processing history, original literature references
- **Technical metadata**: Measurement techniques, instrumentation, depth intervals, rock types

All metadata conform to international standards (ISO 19115, DataCite) and are exportable in machine-readable formats to ensure interoperability with other geoscientific data services.

#### Quality Assurance Scheme

A cornerstone of the WHDB project is the comprehensive quality evaluation framework developed by the International Heat Flow Commission (IHFC). This scheme addresses the historical challenge that heat-flow data quality has been heterogeneous and poorly documented. The quality framework includes:

- **Standardized quality classifications**: Systematic categorization of data reliability
- **Method documentation requirements**: Comprehensive recording of measurement techniques and corrections
- **Uncertainty quantification**: Proper documentation of measurement uncertainties
- **Peer review workflows**: Community-driven assessment and validation of submitted data
- **Version control**: Transparent tracking of data revisions and quality improvements

This quality-first approach ensures that researchers can confidently use WHDB data for critical applications in geodynamic research, geothermal energy assessment, and subsurface resource management.

## Portal Features and User Services

The WHDB web portal provides a modern, intuitive interface designed to maximize usability for the global geoscientific community.

### Data Discovery and Exploration

- **Faceted search**: Filter by quality criteria, geographic region, measurement methods, authors, temporal range
- **Map-based selection**: Interactive spatial queries for regional data extraction
- **Keyword search**: Free-text search across metadata and literature references
- **Statistical visualizations**: Descriptive statistics with uncertainty representations
- **Spatial interpolations**: Global heat-flow maps using spherical harmonic analysis

### Data Visualization Tools

- **Digital borehole profiles**: 1D thermal profiles showing temperature-depth relationships
- **Thermal cross-sections**: 2D crustal profiles (e.g., mid-oceanic ridge transects)
- **Comparative analysis**: Overlay of modeled surface heat-flow rasters with observational data
- **Interactive mapping**: Web-based exploration powered by modern GIS technologies

### Data Submission and Curation

The portal supports community contributions through a structured submission system:

- **Template-based upload**: Excel/CSV templates with predefined structures and validation
- **Web form entry**: Manual data entry through guided input forms
- **Automated validation**: Server-side checks for logical consistency, completeness, and accuracy
- **Metadata editor**: Structured metadata capture following international standards
- **Review workflow**: Internal peer review before public release
- **DOI publication**: Direct pathway to formal data publication with citable DOI

### Download and Interoperability

The infrastructure supports diverse data access patterns:

- **Standard formats**: CSV, JSON, XML, GeoJSON, GeoTIFF, netCDF
- **Web services**: WMS (Web Map Service) for spatial visualizations
- **REST API**: Programmatic data access for integration into analysis workflows
- **Full database exports**: Complete data releases for comprehensive analyses
- **Metadata export**: ISO 19115/19139 compliant metadata for catalog integration

## FAIR and Open Science Principles

The WHDB infrastructure embodies FAIR (Findable, Accessible, Interoperable, Reusable) data principles and open science best practices:

- **Findable**: Rich metadata, persistent identifiers, searchable portal, catalog integration
- **Accessible**: Open access portal, RESTful API, standard authentication, long-term GFZ hosting
- **Interoperable**: International standards, multiple format support, linked identifiers
- **Reusable**: Quality documentation, clear licensing, provenance tracking, version control

All data and software developed through the WHDB project are released under open licenses, ensuring that the global research community can freely access, analyze, and build upon this critical scientific resource.

## Community Collaboration and International Support

### Governance and Leadership

The WHDB project is led by the **International Heat Flow Commission (IHFC)**, founded in 1963 under the auspices of the International Association of Seismology and Physics of the Earth's Interior (IASPEI) and promoted by other associations of the International Union of Geodesy and Geophysics (IUGG).

The project benefits from leadership roles held by GFZ researchers:
- **IHFC Database Custodian**: Dr. Sven Fuchs
- **IHFC Secretary**: Dr. Andrea Förster

### Global Data Assessment Network

The data assessment component of the WHDB project is supported by the **Global Heat Flow Data Assessment Group**, comprising over 66 scientists from all continents who have committed to collaborative data revision and quality improvement. This international network was formalized through:

- **ILP Task Force VIII**: International Lithosphere Program Task Force on Global Heat Flow Data Assessment
- **Community workshops**: Regular project workshops and stakeholder meetings (2022-present)
- **International conferences**: IUGG, EGU, IAGA/IASPEI meetings featuring WHDB sessions

### Institutional Partners and Supporters

The project has received formal support letters and active collaboration from leading international organizations:

- International Union of Geodesy and Geophysics (IUGG)
- International Association of Seismology and Physics of the Earth's Interior (IASPEI)
- International Heat Flow Commission (IHFC)
- International Lithosphere Program (ILP)
- Numerous national geoscientific research institutions worldwide

## Organizational Attribution

### GFZ German Research Centre for Geosciences

The **GFZ German Research Centre for Geosciences** (Helmholtz Centre Potsdam) serves as the primary institutional home for the WHDB project and will provide permanent operational hosting and maintenance of the infrastructure beyond the DFG funding period.

**GFZ Contributions**:

- **Project Leadership**: Principal investigators, IHFC representatives, project coordination
- **Technical Infrastructure**: Database development, server hosting, backup systems, security
- **Data Services**: GFZ Data Services provides DOI minting, IGSN management, metadata services
- **Research Expertise**: The Section "Geoenergy" working group on "Exploration of thermal geosystems" brings decades of heat-flow research experience
- **Library and Information Services**: Leading expertise in research data management, persistent identifiers (pioneered STD-DOI concept), and open science frameworks
- **International Networks**: Active roles in NFDI4Earth, Research Data Alliance, World Data System, CODATA, COPDESS

GFZ's Library and Information Services (LIS) has been a driving force in research data management for over 20 years, with groundbreaking contributions including the invention of the DOI for data (STD-DOI, Klump et al., 2006) and development of critical infrastructure for re3data (Registry of Research Data Repositories) and IGSN services.

### Technical University of Dresden

**TU Dresden** (Chair of Geoinformatics, Faculty of Environmental Sciences) provides specialized expertise in web-based geoinformation systems and research data infrastructures.

**TUD Contributions**:

- **Geoinformatics Expertise**: Web-based portals, spatial data infrastructures, GIS technologies
- **Visualization Development**: Interactive mapping tools, data exploration interfaces
- **Usability Engineering**: User-centered design, usability testing, interface optimization
- **Standards Implementation**: OGC services, INSPIRE compliance, international interoperability
- **Research Data Management**: Metadata systems, provenance tracking, quality assurance tools

TU Dresden's Chair of Geoinformatics has extensive experience coordinating scientific data infrastructures (GLUES project, COLABIS, EXTRUSO, GeoKur) and maintains strong connections to national and international networks including AGILE, iEMSs, GDI-DE, INSPIRE, GEOSS, and OGC.

### University of Bremen / MARUM

**MARUM - Center for Marine Environmental Sciences** at the University of Bremen joined as a partner in Phase Two, bringing critical expertise in marine geosciences and oceanographic data management.

**MARUM Contributions**:

- **Marine Heat-Flow Integration**: Bridging continental and oceanic heat-flow data communities
- **Oceanographic Standards**: Implementing marine data standards and best practices
- **IODP Collaboration**: Connections to International Ocean Discovery Program data systems
- **Cross-Disciplinary Expertise**: Integrating geoscience and oceanography research domains

## Long-Term Sustainability

Following the completion of the DFG funding period, the WHDB infrastructure will transition to permanent operational status as a core service of GFZ German Research Centre for Geosciences. This ensures:

- **Institutional commitment**: Long-term hosting by a Helmholtz Centre with stable government funding
- **Operational continuity**: Dedicated staff from GFZ Library and Information Services and Geoenergy sections
- **Technical maintenance**: Ongoing software updates, security patches, infrastructure improvements
- **Data stewardship**: Continuous quality assurance, community engagement, data publication support
- **Scientific relevance**: Integration with evolving research priorities and technological advances

The infrastructure is designed for interoperability with emerging national and international data initiatives, including NFDI4Earth (Germany's National Research Data Infrastructure for Earth System Sciences) and EPOS (European Plate Observing System), ensuring its continued relevance in the evolving landscape of geoscientific research data management.

## Impact and Scientific Value

The WHDB project addresses a critical gap in geoscientific infrastructure by providing:

- **Comprehensive global coverage**: Integration of over a century of heat-flow measurements
- **Quality-assured data**: Systematic evaluation and documentation of data reliability
- **Modern accessibility**: User-friendly web portal with advanced search and visualization
- **Citable datasets**: DOI-based publication enabling proper research attribution
- **Interoperable infrastructure**: Standards-based integration with global research systems

These capabilities support diverse research applications:

- **Geodynamic studies**: Understanding Earth's thermal evolution and lithospheric processes
- **Geothermal energy**: Resource assessment and sustainable energy development
- **Climate research**: Paleoclimatic analysis through borehole temperature data
- **Subsurface storage**: Site characterization for energy and waste storage
- **Natural hazard assessment**: Thermal constraints on tectonic and volcanic systems

By providing the geoscientific community with reliable, well-documented, and easily accessible heat-flow data, the WHDB project enables transformative research addressing fundamental questions about Earth system processes and societal challenges related to sustainable energy and resource management.

## References and Further Information

- **Project Website**: [https://heatflow.world](https://heatflow.world)
- **Data Portal**: [https://portal.heatflow.world](https://portal.heatflow.world)
- **GFZ Project Page**: GEPRIS project 491795283
- **International Heat Flow Commission**: [https://ihfc-iugg.org](https://ihfc-iugg.org)

### Key Publications

- Fuchs, S., et al. (2021): A new database structure for the IHFC Global Heat Flow Database. *International Journal of Terrestrial Heat Flow and Applications*, 4(1), doi: 10.31214/ijthfa.v4i1.62
- Fuchs, S., Norden, B., et al. (2023): Quality-assurance of heat-flow data: The new structure and evaluation scheme of the IHFC Global Heat Flow Database. *Tectonophysics*, doi: 10.1016/j.tecto.2023.229976
- Neumann, F., et al. (2025, PREPRINT): The 2024 Release of the Global Heat Flow Database (GHFDB): Quality Assessment, Metadata Standards, and a Century of Geothermal Data. *Earth System Science Data*, doi: 10.5194/essd-2025-341

### Data Releases

- Global Heat Flow Data Assessment Group (2024): The Global Heat Flow Database: Release 2024. GFZ Data Services, doi: 10.5880/dgeo.2024.014
- Fuchs, S., et al. (2023): The Global Heat Flow Database: Update 2023. GFZ Data Services, doi: 10.5880/dgeo.2023.008
