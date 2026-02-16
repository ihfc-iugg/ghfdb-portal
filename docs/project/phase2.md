# Phase 2 Project

## WP1: Data Portal Backend, Architecture & Interoperability

**Lead:** GFZ-LIS (Kirsten Elger)
**Involved:** TUD
**Timeline:** M1–M36
**Personnel:**

- Samuel Jennings - Main developer for WP1, WP2

### Objectives

1. Consolidate the technical backbone of the web-based data portal
2. Enhance DOI-minting service (semi-automatized data publication process)
3. Enable interoperability to other geoscientific data services
4. Provide full database documentation

### Description

WP1 comprises several strategic steps aimed at consolidating the database and the technical backbone of the web-based data platform and enhancing it with new impactful functionalities.

#### Key Initiatives

1. **Improved resilience of the technical infrastructure**
2. **Improved (semi-automatized) data-publication process**
3. **Extended database structure, metadata schemes, and quality procedures for supportive data**

#### Detailed Scope

#### Database Consolidation & Extensions

- Consolidation of the main database and backbone infrastructure parameters for heat flow (thermal rock properties and subsurface temperature)
- Extension for storing information on computational spatial 2D grids of temperature and (surface) heat flow produced using:
  - Numerical computer models (forward and inverse)
  - Statistical models (ML/AI)
- Modification of upload and download functionality for grid data
- Development of adequate metadata schemes through community-driven workflow (with WP3)

#### Data Publication & Persistent Identifiers

- Extended data connection to:
  - Literature references (DOI where available)
  - Authors and institutes (ORCID and ROR where available)
  - Rock samples (IGSN where available)
- Semi-automated DOI minting service completion
- Enhanced data publication workflows

#### Community & Code Integration

- User-driven code collection of specific data processing codes
- Upload or interlinkage to existing GitHub repositories
- Graphical user interface extension (WP2) to display new selector variables

#### Infrastructure Resilience

- Comprehensive testing and code documentation
- System stability improvements
- Enhanced security protocols

### Deliverables

*Note: Specific WP1 deliverables are not explicitly enumerated in the Phase 2 project description. WP1 contributes to global project deliverables:*

- **D6** - Full global heat flow dataset updated (M33)
- **D7** - Final release of data portal operating (M34)
- **D8** - Final project report (M36)

### Tasks

*Tasks to be defined as project progresses*

### Cross-Package Dependencies

### WP1 → WP2 (User Interface)

- WP1 provides API endpoints and data structures
- WP1 provides selector variables for GUI display
- WP1 provides grid data visualization capabilities

### WP3 → WP1 (Continental Data)

- WP3 community-driven workflow defines metadata schemes for WP1 implementation
- WP3 quality procedures inform database structure

### WP4 → WP1 (Marine Data)

- WP4 requirements inform selector variables
- WP4 metadata needs influence database design

### Success Criteria

- Technical backbone consolidated and documented
- DOI minting service operational
- Database extended for new data types (properties, temperature, grids)
- Interoperability with other geoscientific data services achieved
- Full database documentation completed
- Code repository integration functional

---

## WP2: Data Portal Front End, Exploration, Visualization & Mapping

**Lead:** TUD (Stephan Mäs)
**Involved:** GFZ
**Timeline:** M1–M36
**Personnel:**

- Nikolas Ott (Scientist, 100%, 18 PM) - Lead and work of WP2, support WP1
- Student Worker (40h/month, 12 months) - Tool programming and usability evaluation

### Objectives

Consolidation and strengthening the web-based front-end for the data portal, including the user interface, functionalities, analysis, visualizations, and mapping functionalities.

### Description

WP2 comprises several strategic steps to consolidate and improve the web-based data platform.

#### Key Initiatives

1. **API conformance**
2. **Improved analytical tools**
3. **Expanded educational resources**
4. **Plugin development**
5. **UI update**

#### Detailed Scope

##### API Conformance

- Ensure conformance to STAC standard
- Ensure conformance to OpenAPI
- Implement latest relevant OGC API features for heat flow (point) data
- Facilitate interoperability with various geospatial data platforms
- Develop comprehensive API documentation and developer guides
- Streamline integration with external systems
- Continuous monitoring of industry trends and standards updates

##### Analytical Tools Enhancement

- Technical improvements to existing 2D data profile plots:
  - Boreholes (computed heat-flow and temperature-depth profiles)
  - Cross sections (computed heat-flow profiles)
- Methodological enhancements:
  - Validation mechanisms to ensure accuracy
  - User-driven implementation of spatial or parameter data for computation
  - Updated analytical algorithms reflecting advancements in heat flow processing
  - Improved usability
- Establish feedback sessions to refine and optimize tools based on user needs

##### Educational Resources

- Implementation of tutorials and webinars
- Provide use-case examples and real-world datasets
- Hands-on learning of platform functionalities and heat-flow data analysis
- Jupyter Notebook integration for Python-based heat-flow processing
- Support user engagement and strengthen practice around data analysis and visualization
- Collaborative projects and shared repositories

##### Plugin Development

- Develop GIS plugin (ArcMap or QGIS) to implement data into professional GIS applications
- Support interoperability and reuse of data
- Provide user-friendly documentation and tutorials for plugin implementation
- Provide documentation for API access

##### UI Update

- Evaluate user-centered design principles
- Refresh and update the UI
- Focus on intuitive navigation, visual appeal, and enhanced user experience
- Interactive elements (context menus, time sliders, etc.)

### Deliverables

- **D2.1** - GIS plugin (M6)
- **D2.2** - Consolidated data portal and user interface (M18)
- **D2.3** - Education tutorial (M12)
- **D2.4** - Documentation (M18)

### Tasks

- T2.1 - API programming (TUD)
- T2.2 - Programming analytical tools (TUD)
- T2.3 - Visualization & UI programming (TUD)
- T2.4 - Programming QGIS plugin (TUD)
- T2.5 - Refreshing and updating UI (TUD)
- T2.6 - Completing documentation (TUD+GFZ)

### Cross-Package Dependencies

#### WP1 → WP2 (Backend)

- WP1 provides API endpoints and data structures
- WP1 provides selector variables for GUI display
- WP1 provides grid data visualization capabilities

#### WP3 → WP2 (Continental Data)

- WP3 provides additional selector variables for faceted search
- WP3 quality flags and data status inform UI features

#### WP4 → WP2 (Marine Data)

- WP4 marine-specific selector variables for GUI integration

### Success Criteria

- API conformance achieved (STAC, OpenAPI, OGC)
- Analytical tools enhanced and validated
- GIS plugin operational
- Educational resources implemented
- UI updated with improved user experience
- Comprehensive documentation completed
