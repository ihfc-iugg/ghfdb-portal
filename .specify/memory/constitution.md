<!--
SYNC IMPACT REPORT (Constitution Update)
===========================================
Version: 1.1.0
Date: 2026-01-02
Type: MINOR (add Test-Driven Development principle and Documentation Standards principle)

PRINCIPLES ADDED:
- VII. Test-Driven Development (new - pytest-based TDD mandate)
- VIII. Documentation Standards (new - comprehensive documentation requirements for FairDM models)

SECTIONS UPDATED:
- Core Principles (added two new principles)
- Technology Stack & Standards (expanded testing requirements to reference Principle VII)
- Development Workflow (expanded documentation requirements to reference Principle VIII)

TEMPLATE IMPACT:
- .specify/templates/plan-template.md - Constitution Check updated to include TDD and documentation gates
- .specify/templates/spec-template.md - no change required (already includes test scenarios)
- .specify/templates/tasks-template.md - no change required (already includes test task examples)

RUNTIME DOC IMPACT:
- docs/guides/testing-standards.md - should be created to document pytest conventions and TDD workflow
- docs/guides/documentation-standards.md - should be created to document FairDM registration requirements
- CONTRIBUTING.md - should be updated to reference new principles VII and VIII

DEFERRED ITEMS:
None - all placeholders filled with project-specific values

FOLLOW-UP ACTIONS:
- Create docs/guides/testing-standards.md with pytest setup, fixtures, and TDD examples
- Create docs/guides/documentation-standards.md with FairDM model registration and documentation patterns
- Update CONTRIBUTING.md to emphasize test-first development and documentation expectations
- Consider adding pre-commit hooks to verify test coverage thresholds
-->

# Global Heat Flow Database Portal Constitution

## Core Principles

### I. Schema Fidelity to GHFDB Standards

The portalâ€™s **canonical** data model **MUST** be a modern, normalized relational schema designed for correctness,
maintainability, and usability.

The IHFC GHFDB conceptual schema (as published in the references below) **MUST** be treated as an
interchange/publishing format (â€œproductâ€) that the portal can reliably import from and export to:

- Fuchs et al. (2021): *A new database structure for the IHFC Global Heat Flow Database*
- Fuchs et al. (2023): *The Global Heat Flow Database: Update 2023*

**Non-negotiable requirements:**

- The portal database schema is authoritative for internal storage and MUST prioritize relational best practices (normalization, provenance, extensibility)
- Import/export tooling MUST provide a deterministic mapping between the portal schema and the IHFC GHFDB schema (see Principle III)
- â€œMandatoryâ€ (M) fields in the IHFC schema MUST NOT be blindly enforced as hard requirements for portal UI data entry when they would block reasonable workflows
- The portal MUST support capturing incomplete records and MUST track completeness/state such that stricter requirements can be enforced at publish/export time
- Quality scoring (U-score, M-score) and correction flags MUST implement the official evaluation scheme and MUST export to IHFC-compatible fields
- Any material divergence from the IHFC schema MUST be documented (mapping docs + release notes) with rationale

**Semantic obligations (what MUST be preserved even if implemented differently):**

- The portal MUST preserve the scientific meaning of the GHFDB parent/child structure (site â†’ interval â†’ measurement), even if internal normalization differs
- The portal MUST preserve the intended quality relevance of fields (U-score fields, M-score fields, perturbation/correction flags), even if internal storage differs
- Administrative/review metadata (e.g., reviewer name, review date, reviewer comments) MUST be treated as privileged editorial data and MUST NOT be conflated with scientific measurement metadata

**Persistent identifiers (PIDs) are first-class metadata:**

- DOI MUST be supported end-to-end (capture, storage, and export) to link heat-flow records to primary literature where available
- ORCID MUST be supported end-to-end for contributor/author identification where available
- IGSN MUST be supported where applicable to link measurements to physical samples
- ROR MUST be supported for research organization affiliations

**Rationale:** The portalâ€™s job is to implement the community intent of the GHFDB in a maintainable, usable system.
Treating the IHFC schema as an interchange â€œproductâ€ enables rigorous publication compatibility without inheriting
spreadsheet-era constraints that harm UI workflows or long-term maintainability.

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

The portal **MUST** document and expose the mapping between the flat GHFDB conceptual schema
(spreadsheet template / interchange format) and the underlying normalized relational database schema.

**Documentation requirements:**

- Maintain [docs/ghfdb_fields.md](docs/ghfdb_fields.md) with a complete mapping table showing:
  - GHFDB field name â†’ Database table â†’ Django model â†’ Accessor path â†’ Declaring model
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
- Literature-derived data enrichment and quality control SHOULD follow a â€œfour-eyes principleâ€ (independent verification) where feasible

**Terminology clarification:**

- â€œLiterature reviewâ€ refers to the WHDB data assessment activity of extracting/curating data from publications
- â€œPublication approval reviewâ€ refers to portal administrator approval required before any dataset becomes public

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

### VI. Provenance, Attribution & Review Governance (NON-NEGOTIABLE)

The initial portal release is designed to support the WHDB data assessment workflow, where **reviewers**
systematically analyze historic publications to extract data and metadata.

The portal MUST support two distinct review processes with unambiguous provenance tracking:

1. **Literature assessment review (curation)**: reviewers extract/curate data from a publication.
2. **Publication approval review (editorial/admin)**: administrators decide whether a dataset can become public.

**Non-negotiable provenance and attribution requirements:**

- Datasets derived from literature MUST retain an accurate record of the original publication (bibliographic reference and DOI where available)
- The portal MUST record original scientific contributors (authors) separately from portal contributors (reviewers/curators/editors)
- The portal MUST record all participants in the assessment workflow (reviewers, collaborators) as contributors with appropriate roles
- The portal MUST record administrative/editorial actions taken during publication approval (approver identity and timestamp at minimum)
- Provenance metadata MUST be preserved across import/export and public publishing so that downstream users can attribute work correctly

**Publication gating and role hierarchy requirements:**

- No uploaded dataset MAY become public without explicit approval by authorized portal administrators
- The portal MUST enforce a strict hierarchy of roles/permissions for administrative actions (e.g., not all staff can approve publication)
- Permission to approve publication MUST be separable from permission to curate/submit a dataset for review
- Role assignments and permission changes MUST be restricted to a small set of high-privilege administrators

**Rationale:** Reviewers often do not own the underlying data they curate, but they provide essential scholarly labor.
Accurate provenance preserves scientific attribution to original authors while crediting assessment contributors and ensuring
that public releases meet administrative review standards.

### VII. Test-Driven Development (NON-NEGOTIABLE)

The portal **MUST** follow test-driven development (TDD) practices using pytest as the testing framework.

**Test-first development requirements:**

- New features and bug fixes MUST begin with a failing test that defines expected behavior
- Tests MUST be written before implementation code (red-green-refactor cycle)
- All tests MUST pass before code can be merged to main branch
- Pull requests MUST include both test code and implementation code together

**Testing framework and conventions:**

- **Framework:** pytest (required) with appropriate plugins (pytest-django, pytest-cov, pytest-mock)
- **Structure:** Organize tests to mirror application structure (`tests/test_ghfdb/`, `tests/test_heat_flow/`)
- **Fixtures:** Use pytest fixtures for common test data; share fixtures via `conftest.py`
- **Naming:** Test functions MUST start with `test_` and describe what they verify (e.g., `test_heat_flow_calculation_with_valid_inputs`)
- **Coverage:** Aim for >80% code coverage; critical paths (data validation, calculations, exports) MUST have 100% coverage

**Test categories:**

- **Unit tests:** Test individual functions/methods in isolation using mocks for dependencies
- **Integration tests:** Test interaction between components (models, services, database)
- **Contract tests:** Verify API endpoints match published contracts
- **End-to-end tests:** Test complete workflows (template upload â†’ validation â†’ export)

**Quality gates:**

- CI/CD pipeline MUST run full test suite on every commit
- Test failures MUST block merges
- Decreasing coverage MUST block merges
- All Django model changes MUST include migration tests
- All FairDM model registrations MUST include model validation tests

**Rationale:** TDD ensures correctness, prevents regressions, and provides living documentation of system behavior. For a scientific data portal, rigorous testing is essential to maintain data integrity and user trust. pytest's fixture system and Django integration make it ideal for testing FairDM-based applications.

### VIII. Documentation Standards (NON-NEGOTIABLE)

The portal **MUST** maintain comprehensive documentation for all specifications, features, and data models.

**Specification documentation requirements:**

- Every feature MUST have a specification document in `/specs/[###-feature-name]/spec.md` following the spec template
- Specifications MUST include user stories with acceptance criteria written in Given-When-Then format
- Specifications MUST be written before implementation begins
- Specification updates MUST be committed alongside implementation changes

**Data model documentation requirements:**

- Every Django model MUST have a comprehensive docstring explaining its purpose and scientific context
- Every model field MUST have a `help_text` parameter describing its meaning and constraints
- Complex models MUST have a data model diagram in `/specs/[###-feature-name]/data-model.md`
- Model relationships (ForeignKey, ManyToMany) MUST document the semantic meaning of the relationship

**FairDM registration documentation requirements:**

- Every model registered with FairDM (`@fairdm.register`) MUST document:
  - Which FairDM base class it extends and why
  - What FairDM features it uses (admin mixins, table classes, API endpoints)
  - Any FairDM configuration or customization applied
- FairDM model registrations MUST include inline comments explaining non-obvious configuration choices
- Custom FairDM admin classes MUST document what UI/UX behaviors they provide

**API and contract documentation:**

- Every API endpoint MUST have an OpenAPI/Swagger spec in `/specs/[###-feature-name]/contracts/`
- API documentation MUST include example requests and responses
- Breaking API changes MUST be documented in release notes with migration guidance

**User-facing documentation:**

- New features MUST include updates to `/docs/` with user guides and screenshots where appropriate
- GHFDB schema changes MUST update `/docs/ghfdb_fields.md` with field mapping tables
- Template parser changes MUST update `/docs/guides/importing-data.md`

**Code documentation:**

- Complex algorithms MUST include inline comments explaining the approach and any scientific/mathematical basis
- Non-obvious design decisions MUST be documented in code comments or architecture decision records (ADRs)
- Public functions and classes MUST have docstrings following PEP 257 conventions

**Rationale:** Comprehensive documentation is essential for maintainability, onboarding new contributors, and ensuring scientific reproducibility. FairDM's framework nature makes clear registration documentation critical for understanding which features come from the framework versus custom implementations. For a long-term research infrastructure, documentation is as important as the code itself.

## Technology Stack & Standards

**Required Technologies:**

- **Language:** Python â‰¥3.13
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

**Testing Standards (see Principle VII):**

- **Framework:** pytest with pytest-django, pytest-cov, pytest-mock
- **Command:** `poetry run pytest` (run full suite)
- **Coverage:** `poetry run pytest --cov=project --cov-report=html`
- **Fixtures:** Centralize in `tests/conftest.py` and app-specific `conftest.py` files
- **Naming:** `test_<function_name>_<scenario>` (e.g., `test_heat_flow_validation_with_missing_fields`)
- **Test Data:** Use fixtures for sample GHFDB data; commit fixtures to `fixtures/` directory
- **Mocking:** Prefer pytest-mock over unittest.mock for Django compatibility

**Versioning:**

- **Format:** CalVer (`YYYY.WW`) for portal releases
- **Schema Migrations:** Django migrations with descriptive comments
- **API Versioning:** Follow FairDM REST API versioning strategy

## Development Workflow

**Branching & Contributions:**

- Development led by the World Heat Flow Database Project (WHFDB)
- Community contributions (bug fixes) welcome; new features require maintainer approval
- Fork repository â†’ Create feature branch â†’ Submit pull request
- Branch naming: descriptive (e.g., `fix-template-parser`, `add-quality-filters`)

**Testing Requirements (see Principle VII):**

- **Test-first development:** Write failing tests before implementation (TDD)
- **Coverage threshold:** Maintain >80% overall coverage; 100% for critical paths
- **Test all layers:** Unit tests for functions/methods, integration tests for workflows, contract tests for APIs
- **Run locally:** `poetry run pytest` before every commit
- **CI enforcement:** All tests must pass; coverage must not decrease
- **Django-specific:** Test models, views, forms, admin, management commands, and migrations
- **FairDM-specific:** Test model registrations, admin customizations, and FairDM API integrations
- **Critical workflows:** Template upload/export, quality scoring, and publication workflows require end-to-end tests

**Code Review:**

- All changes require pull request review
- Reviewers verify:
  - GHFDB interchange compatibility (import/export mapping and round-trip integrity)
  - FairDM integration (no custom reimplementations)
  - Documentation updates (especially for schema changes)
  - Test coverage for new functionality
- Maintainers hold final merge authority

**Documentation (see Principle VIII):**

- **Specifications:** Every feature requires `/specs/[###-feature-name]/spec.md` with user stories and acceptance criteria
- **Data models:** Complex models require data model diagrams and relationship documentation
- **FairDM registrations:** Document which FairDM base classes are used and why, plus any customizations
- **Code documentation:** Docstrings for all public APIs (PEP 257), inline comments for complex logic
- **User guides:** Update [docs/](docs/) for user-facing features with screenshots and examples
- **Field mappings:** Schema changes require [docs/ghfdb_fields.md](docs/ghfdb_fields.md) updates
- **API contracts:** API endpoints require OpenAPI specs in `/specs/[###-feature-name]/contracts/`
- **Contributors:** Maintain [CONTRIBUTORS.md](CONTRIBUTORS.md) with all contributors
- **Process:** Update [CONTRIBUTING.md](CONTRIBUTING.md) for process changes

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

**Role & Permission Governance:**

- The portal MUST implement least-privilege permissions and role-based access control for reviewer and administrator capabilities
- Publication approval authority MUST be limited to explicitly designated administrative roles
- Administrative role hierarchy MUST be documented and reviewed periodically as part of compliance review

**Funding & Institutional Alignment:**

- This project is funded by the Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) under project number 491795283
- Hosted and maintained by GFZ German Research Centre for Geosciences
- Governed by the International Heat Flow Commission (IHFC-IUGG)
- All development decisions must align with DFG grant objectives and open science requirements

**Sustainability commitment:**

- GFZ has committed to sustainably operate the research data infrastructure in-house beyond the initial grant period; architectural decisions MUST support long-term maintainability and institutional operation

**Version**: 1.1.0 | **Ratified**: 2026-01-02 | **Last Amended**: 2026-01-02

