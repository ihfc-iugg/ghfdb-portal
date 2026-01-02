<!--
SYNC IMPACT REPORT (Constitution Update)
===========================================
Version: 1.0.0 → 1.1.0
Date: 2026-01-02
Type: MINOR (WHDB Phase 1 evidence + infrastructure requirements)

PRINCIPLES UPDATED:
- I. Schema Fidelity to GHFDB Standards (parent/child obligations, PID requirements)
- IV. Open Science & Data Quality (GFZ Data Services DOI publication + validation workflow)
- Technology Stack & Standards (production architecture requirements)

SECTIONS UPDATED:
- Core Principles
- Technology Stack & Standards
- Funding & Institutional Alignment

TEMPLATE IMPACT:
✅ plan-template.md - aligned with schema fidelity and FairDM principles
✅ spec-template.md - updated to include schema mapping requirements
✅ tasks-template.md - task categories reflect GHFDB, schema, and community tasks
✅ commands/*.md - no agent-specific references found; generic guidance retained

DEFERRED ITEMS:
None - all placeholders filled with project-specific values

FOLLOW-UP ACTIONS:
- Ensure docs/whdb_project.md stays aligned with WHDB reports
- Consider correcting Poetry metadata license/classifiers to match LICENSE
-->

# Global Heat Flow Database Portal Constitution

## Core Principles

### I. Schema Fidelity to GHFDB Standards

All database models **MUST** faithfully implement the conceptual metadata structure defined by the International Heat Flow Commission (IHFC) in:

- Fuchs et al. (2021): *A new database structure for the IHFC Global Heat Flow Database*
- Fuchs et al. (2023): *The Global Heat Flow Database: Update 2023*

**Non-negotiable requirements:**

- Every Django model corresponds to a documented entity in the GHFDB schema (parent/child heat flow structure, sites, intervals, measurements)
- Field names, constraints, and relationships align with published GHFDB specifications
- Quality scoring (U-score, M-score) and correction flags implement the official evaluation scheme
- Database table comments reference the corresponding GHFDB schema section

**Schema structure obligations (conceptual metadata structure):**

- The portal MUST preserve the GHFDB parent/child level structure, including which fields are mandatory, recommended, or optional (M/R/O)
- The portal MUST preserve the intended quality relevance of fields, including U-score fields, M-score fields, and perturbation/correction flags (P)
- Administrative/review metadata (e.g., reviewer name, review date, reviewer comments) MUST be treated as privileged editorial data and must not be conflated with scientific measurement metadata

**Persistent identifiers (PIDs) are first-class metadata:**

- DOI MUST be used to link each heat-flow record to its primary publication reference where available
- ORCID MUST be used to identify contributors/authors where available
- IGSN MUST be supported to link measurements to physical samples where applicable
- ROR MUST be supported for research organization affiliations

**Rationale:** The portal serves as the authoritative implementation of the community-defined GHFDB structure. Schema fidelity ensures interoperability, reproducibility, and trust across the international heat flow research community.

### II. FairDM Framework Integration

The portal **MUST** leverage the FairDM framework for all core data management, publishing, and community features. Custom implementations are **prohibited** unless FairDM explicitly lacks the capability.

**Required FairDM components:**

- `fairdm` core: Sample, Measurement, Dataset, Project models and admin
- `fairdm-geo`: Geographic features (Point, Borehole), depth intervals
- `fairdm-discussions`: User engagement, comments, follows
- `fairdm-rest-api`: RESTful API for programmatic access

**Integration principles:**

- Extend FairDM base classes (e.g., `HeatFlowSite(Borehole)`, `SurfaceHeatFlow(Measurement)`)
- Register models with FairDM using `@fairdm.register` decorators
- Use FairDM admin mixins and table classes for consistent UI/UX
- Contribute generic improvements back to FairDM repositories when feasible

**Rationale:** FairDM provides battle-tested infrastructure for FAIR data principles, reducing maintenance burden and ensuring consistency with other FairDM-powered portals. Duplicating FairDM features would fragment development effort and create technical debt.

### III. Conceptual vs. Relational Schema Transparency

The portal **MUST** document and expose the mapping between the flat GHFDB conceptual schema (spreadsheet template) and the underlying normalized relational database schema.

**Documentation requirements:**

- Maintain [docs/ghfdb_fields.md](docs/ghfdb_fields.md) with a complete mapping table showing:
  - GHFDB field name → Database table → Django model → Accessor path → Declaring model
- Provide user-facing guidance explaining why the schemas differ (normalization, foreign keys, FairDM abstractions)
- Include Django ORM query examples for common GHFDB field access patterns

**Template parsing obligations:**

- GHFDB Excel template upload **MUST** parse the flat structure into the correct relational tables
- Export functions **MUST** reconstruct the flat GHFDB format from relational data
- Schema mismatches (e.g., fields not directly mappable) **MUST** be documented in release notes

**Rationale:** Users expect the GHFDB spreadsheet structure but the portal requires a normalized relational database for data integrity and FairDM compatibility. Transparent documentation prevents confusion and enables advanced users to query the database directly.

### IV. Open Science & Data Quality (NON-NEGOTIABLE)

The portal **MUST** embody open science principles and enforce rigorous data quality standards.

**Open Science mandates:**

- All GHFDB releases publicly accessible at [portal.heatflow.world](https://portal.heatflow.world)
- Provide an API suitable for metadata and data harvesting by external parties
- Public dataset releases MUST be formally published and archived via GFZ Data Services with DOIs for permanent citation
- Documentation and code are open-source (MIT license)

**Data Quality requirements:**

- Implement automated quality scoring per Fuchs et al. (2023) Section 3.4
- Require metadata standards compliance before dataset publishing
- Provide review workflows with version control for dataset amendments
- Validate uploaded templates against schema constraints before ingestion

**Validation and review workflow requirements (multi-level):**

- New submissions MUST undergo multi-level validation, including database-level constraints, application-level validation, and manual/editorial review
- Literature-derived data enrichment and quality control SHOULD follow a “four-eyes principle” (independent verification) where feasible

**Rationale:** The portal is funded by public research funds (DFG grant 491795283) and serves the global scientific community. Open access, reproducibility, and data integrity are foundational to the project's mission and funding mandate.

### V. Community-Driven Collaboration

The portal **MUST** facilitate researcher engagement, collaboration, and knowledge sharing.

**Community features:**

- User accounts with ORCID integration for identity verification
- Project creation to showcase past/present/future heat flow research
- Dataset contributor management (personal and organizational)
- Follow system for users and projects
- Discussion forums and commenting on datasets/projects

**Collaboration workflows:**

- Early dataset creation encouraged (metadata-only) to signal intent and attract collaborators
- Public issue tracker and discussion forum on GitHub for feature requests
- Community polls to prioritize development roadmap
- Transparent contribution guidelines and code of conduct

**Rationale:** The GHFDB is a community-built resource spanning decades of research. The portal must lower barriers to contribution, recognize all contributors, and foster global collaboration among heat flow researchers.

## Technology Stack & Standards

**Required Technologies:**

- **Language:** Python ≥3.13
- **Framework:** Django 5.0+ with FairDM extension ecosystem
- **Database:** PostgreSQL (production); SQLite (development/testing)
- **Deployment:** Docker containers, hosted on GFZ Potsdam infrastructure
- **Documentation:** Sphinx with sphinx-book-theme
- **Package Management:** Poetry 1.1.0+

**Production architecture (baseline expectations):**

- PostgreSQL SHOULD be paired with PostGIS for geospatial operations
- Redis SHOULD be used for caching and message brokering
- Celery SHOULD be used for asynchronous/background processing (e.g., emails, file processing)
- MinIO (S3-compatible) SHOULD be used for secure object storage of user uploads
- A reverse proxy/load balancer (e.g., Traefik) SHOULD route incoming traffic to services
- Automated backups of database and media MUST run at regular intervals

**Code Standards:**

- **Linting:** Ruff with target-version py311, line-length 120
- **Formatting:** Ruff auto-fix enabled
- **Style:** Follow PEP 8; use Black-compatible formatting
- **Type Hints:** Gradually adopt type annotations for new code

**Versioning:**

- **Format:** CalVer (`YYYY.WW`) for portal releases
- **Schema Migrations:** Django migrations with descriptive comments
- **API Versioning:** Follow FairDM REST API versioning strategy

## Development Workflow

**Branching & Contributions:**

- Development led by the World Heat Flow Database Project (WHFDB)
- Community contributions (bug fixes) welcome; new features require maintainer approval
- Fork repository → Create feature branch → Submit pull request
- Branch naming: descriptive (e.g., `fix-template-parser`, `add-quality-filters`)

**Testing Requirements:**

- Write tests for all new models, views, and parsers
- Run test suite before committing: `poetry run pytest`
- Integration tests required for template upload/export workflows
- Use fixtures for sample GHFDB data

**Code Review:**

- All changes require pull request review
- Reviewers verify:
  - Schema fidelity (references Fuchs et al. where applicable)
  - FairDM integration (no custom reimplementations)
  - Documentation updates (especially for schema changes)
  - Test coverage for new functionality
- Maintainers hold final merge authority

**Documentation:**

- Update [docs/](docs/) for user-facing features
- Update [CONTRIBUTING.md](CONTRIBUTING.md) for process changes
- Maintain [CONTRIBUTORS.md](CONTRIBUTORS.md) with all contributors
- Schema changes require [docs/ghfdb_fields.md](docs/ghfdb_fields.md) updates

## Governance

**Authority & Precedence:**

- This constitution supersedes informal practices and undocumented conventions
- All pull requests, code reviews, and architectural decisions **MUST** verify compliance with core principles
- The WHFDB Project maintainers hold final interpretation authority

**Amendment Process:**

1. Propose amendment via GitHub discussion with rationale
2. Maintainers review for alignment with project mission and DFG funding mandate
3. Approved amendments increment version per semantic rules:
   - **MAJOR:** Principle removal, redefinition, or backward-incompatible governance change
   - **MINOR:** New principle added or materially expanded guidance
   - **PATCH:** Clarifications, typo fixes, non-semantic refinements
4. Update constitution file with new version, amendment date, and sync impact report
5. Propagate changes to affected templates and documentation

**Compliance Review:**

- Quarterly review of recent PRs to verify constitutional adherence
- Annual review of constitution relevance given GHFDB schema updates (Fuchs et al. revisions)
- Major GHFDB schema changes (new publications) trigger constitution review

**Funding & Institutional Alignment:**

- This project is funded by the Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) under project number 491795283
- Hosted and maintained by GFZ German Research Centre for Geosciences
- Governed by the International Heat Flow Commission (IHFC-IUGG)
- All development decisions must align with DFG grant objectives and open science requirements

**Sustainability commitment:**

- GFZ has committed to sustainably operate the research data infrastructure in-house beyond the initial grant period; architectural decisions MUST support long-term maintainability and institutional operation

**Version**: 1.1.0 | **Ratified**: 2026-01-02 | **Last Amended**: 2026-01-02
