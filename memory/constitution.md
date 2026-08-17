<!--
Sync Impact Report
- Version change: 1.0.0 → 1.1.0
- Modified principles: none redefined; Governance "Scope" corrected to name the `ihfc-iugg/ghfdb-portal`
  repository
- Added sections:
    - Principle IX. Simplicity & Maintainability
    - Principle X. Fidelity to the WHDB Project Mission & DFG Funding
- Removed sections: N/A
- Consistency notes:
    - docs/constitution/index.md rewritten as a landing page; it no longer restates the principles, so the two
      copies cannot diverge again. See docs/adr/0008-one-constitution-one-glossary.md.
    - Two governance clauses repointed from the removed vendored toolchain to the files that replaced it:
      docs/development/spec-driven-workflow.md, and AGENTS.md / CONTEXT.md / docs/agents/.
    - Domain vocabulary now lives in CONTEXT.md at the repository root.
- Follow-up TODOs:
    - TODO(RATIFICATION_DATE): Confirm exact project inception/governance date with project lead if 2024-01-01 is incorrect
    - TODO(GOVERNANCE_EXPANSION): When additional maintainers join, formalize stewardship committee and RFC process
    - TODO(I18N_LOCALE_LIST): Enumerate priority translation locales once community survey is complete
-->

# Global Heat Flow Database Portal — Constitution

## Core Principles

### I. FAIR-First Scientific Data

The GHFDB Portal exists to make earth-science heat flow data Findable, Accessible, Interoperable, and Reusable for
researchers, institutions, and the broader public, in compliance with FAIR data principles.

- Every feature MUST be evaluated on how it improves — or at minimum does not weaken — the FAIR characteristics of
  data, metadata, and APIs.
- The portal MUST expose rich, machine-readable metadata for all primary entities (sites, intervals, measurements,
  datasets, contributors, organisations) through both the UI and documented endpoints.
- Persistent, globally recognised identifiers (DOIs for datasets/releases, ORCID for contributors, ROR for
  organisations, IGSNs where applicable) MUST be first-class in the data model and surfaced in all public views.
- Public read access to published releases MUST NOT require user registration or custom client code; data MUST be
  discoverable and downloadable via standard web endpoints.
- FAIR compliance is a NON-NEGOTIABLE design constraint: a minimally configured portal MUST be able to satisfy FAIR
  expectations using core functionality without additional custom development.
- Data provenance MUST be recorded and preserved; every record MUST trace to a contributor, submission, and, where
  available, a citable publication following Fuchs et al. (2021, 2023).

### II. GHFDB Schema Fidelity & Domain Integrity

The portal maintains a canonical, normalised relational schema that faithfully represents the IHFC GHFDB conceptual
model (Fuchs et al., 2021, 2023). The flat spreadsheet distributed by IHFC is an **import/export product**, not the
source of truth.

- The internal relational schema MUST capture the full parent/child conceptual hierarchy defined by the World Heat Flow
  Database Project: site → interval → child measurement, with each IHFC-defined field mapped to an explicit Django
  model field or documented computed accessor.
- Any field listed in the official GHFDB specification (Fuchs et al.) MUST be represented in the Django models.
  Additions beyond the IHFC specification MUST be explicitly justified and documented.
- The field mapping table (`docs/ghfdb_fields.md`) is the authoritative record of how IHFC flat columns map to
  relational model fields. It MUST be kept current whenever models change.
- Schema changes that diverge from the IHFC specification require written justification cross-referenced to the mapping
  documentation and, where the divergence is intentional and permanent, an amendment note in this constitution.
- Scientific metadata (e.g., quality scores, uncertainty ranges, correction flags) MUST be stored at the correct level
  of the hierarchy (site/interval/child) as defined by Fuchs et al. Neither up- nor down-casting of metadata is
  permitted without documented scientific rationale.
- Domain model integrity takes priority over implementation convenience; ORM patterns and query optimisations MUST NOT
  distort the conceptual model.

### III. FairDM-First Integration

The GHFDB Portal is a domain-specific configuration of the FairDM framework, not a standalone Django project.
Custom re-implementation of features already provided by FairDM MUST be avoided.

- All primary scientific models (HeatFlowSite, HeatFlowInterval, ParentHeatFlow, HeatFlow and related measurements)
  MUST extend the appropriate FairDM base classes (`Sample`, `Measurement`, etc.).
- Models MUST be registered with the FairDM registry using `@fairdm.register`, exposing FAIR infrastructure (list
  views, admin, filtering, tables, serialisers) without custom view plumbing.
- FairDM-provided forms, tables, filters, serialisers, and admin integrations MUST be used as the default; custom
  overrides are permitted only where GHFDB-specific requirements cannot be satisfied by configuration.
- The FairDM ecosystem packages (`fairdm-geo`, `fairdm-discussions`, etc.) SHOULD be adopted for functionality they
  provide rather than creating bespoke equivalents.
- When FairDM changes its API or recommended patterns, all GHFDB code MUST be updated in the same pull request to
  maintain clean integration.

### IV. Open Science, Provenance & Review Governance

The portal supports the World Heat Flow Database Project's commitment to open science, reproducible research, and
rigorous data curation aligned with DFG grant requirements.

- All published dataset releases MUST be publicly accessible without authentication, subject to an appropriate open
  data licence (e.g., CC BY 4.0 or equivalent).
- A governed review workflow MUST ensure that data is curated and admin-approved before publication; direct
  contributor-to-public publication without review is PROHIBITED.
- Contributor attribution MUST be maintained throughout the record lifecycle; deletions of contributor attribution
  fields are PROHIBITED.
- Data management practices MUST comply with DFG data management requirements (grant 491795283) and the IHFC's
  community standards for data submission and citation.
- Security and privacy controls MUST be applied to unpublished/in-review data so that unauthenticated users cannot
  access records that have not been approved for public release.
- The portal MUST support citation of datasets (e.g., via DataCite-compatible metadata) so that researchers can
  receive credit for their contributions.

### V. Internationalisation & Global Accessibility

The Global Heat Flow Database serves an international scientific community. The portal MUST be designed to support
multiple languages and accessible to users regardless of locale.

- All user-facing strings in templates, views, models, and admin MUST be wrapped in Django's translation utilities
  (`_()`, `gettext_lazy`, `ngettext`) to enable localisation.
- No hard-coded natural-language strings (error messages, labels, help texts, button labels) are permitted outside of
  translation wrappers — this rule has ZERO exceptions for user-visible strings.
- Locale-sensitive formatting (dates, numbers, units) MUST use Django's `USE_I18N = True` / `USE_L10N = True`
  settings and Django's format localisation utilities rather than hard-coded Python format strings.
- All scientific units displayed in the UI MUST be labelled unambiguously; where SI and non-SI variants exist, the
  canonical IHFC unit convention (as defined in Fuchs et al.) MUST be used with clear labelling.
- New UI components, templates, and Cotton components MUST include i18n-ready strings from the moment they are
  introduced; retrofitting i18n is costly and error-prone.
- Translation files (`.po`/`.mo`) MUST be maintained in the repository; at minimum, English (`en`) is the baseline;
  additional languages MAY be contributed by the community.
- Accessibility (WCAG 2.1 AA) is treated alongside i18n as a non-optional quality dimension: regressions in keyboard
  navigation, contrast ratios, or semantic HTML are treated as bugs.

### VI. Test-First Quality & Sustainability (NON-NEGOTIABLE)

The GHFDB Portal is long-lived scientific infrastructure. All behaviour changes MUST be driven by tests written first
and must maintain high standards of reliability, type safety, and style.

**Test-First Discipline**:

- Tests MUST be written and observed failing before implementation work begins (Red → Green → Refactor).
- All new or changed Python behaviour MUST have pytest coverage.
- Django integration behaviour MUST have pytest-django coverage with appropriate test database strategies.
- Scientific correctness tests (e.g., round-trip import/export, quality score calculations, schema mapping) MUST be
  written as explicit regression tests with known inputs and expected outputs derived from Fuchs et al.
- Pull requests MUST NOT be merged with failing tests, or without new/updated tests for behaviour changes.
- The only acceptable exception is a docs-only change with no runtime behaviour impact.

**Code Quality & Tooling**:

- Type hints are REQUIRED for all new Python code. Mypy MUST report no new errors for changed files.
- Ruff linting and formatting rules (as defined in `pyproject.toml`) MUST pass for all changed files.
- Test organisation MUST mirror the `project/` source tree under `tests/` with `test_` prefixes at each level.
- Fixture factories MUST use factory-boy and pytest fixtures for reusable, composable test data.
- Performance tests MUST use deterministic guards (e.g., query-count assertions via `django_assert_num_queries`) rather
  than wall-clock timing.
- Coverage is a guide to find untested paths, not a merge gate. Tests MUST be meaningful, maintainable, and reliable.

**Schema-Mapping Test Obligation**:

- Any feature that adds or changes GHFDB field mappings MUST include an automated test verifying the mapping is correct
  end-to-end (model → serialiser/export → flat row, and flat row → importer → model).
- Quality score calculation functions MUST have unit tests with at least two example inputs (from Fuchs et al. where
  available) and their expected outputs pinned as regression tests.

### VII. Documentation Critical

Documentation is part of the portal's scientific output and MUST be treated with the same rigour as code.

- Every public model field, setting, API endpoint, and schema mapping MUST be documented with a reference to the
  relevant IHFC specification section (Fuchs et al., 2021, 2023) where applicable.
- The field mapping table (`docs/ghfdb_fields.md`) MUST be updated in the same pull request as any schema change.
- New public settings, template blocks, and public APIs MUST include at least one minimal usage example in the docs.
- Breaking changes MUST include migration guides with step-by-step upgrade instructions.
- Documentation MUST be versioned alongside code releases.
- Docstrings for GHFDB domain models SHOULD cite the relevant Fuchs et al. paper section and field name to maintain
  a direct link between code and the authoritative scientific specification.

### VIII. Spec-Driven Development Workflow

All non-trivial changes MUST follow the spec-driven workflow documented in
`docs/development/spec-driven-workflow.md`, producing discoverable, version-controlled design artefacts.

- Non-trivial changes MUST start with a feature specification (`spec.md`) that articulates user stories, priorities,
  and measurable success criteria in scientific and user-journey terms.
- User stories MUST be independently testable slices of value, ordered by priority (P1, P2, P3, …).
- Each feature MUST include an implementation plan (`plan.md`) recording technical context, chosen architecture, and
  a "Constitution Check" section that explicitly notes alignment with the Core Principles above.
- Tasks (`tasks.md`) MUST be grouped by user story to enable independent implementation, testing, and delivery.
- **Django System Checks**: `python manage.py check` MUST pass between completing user stories or major
  implementation phases. All system check errors MUST be fixed before proceeding.
- **Validation Frequency**: For multi-phase implementations, run system checks after each phase; test FairDM
  registry integration immediately after modifying models or configuration classes.
- Documentation MUST be updated as features are implemented, not deferred to the end.

### IX. Simplicity & Maintainability

The portal is maintained by a small team over a long horizon. The simplest implementation that satisfies the
requirement is the correct one, and added complexity MUST be justified rather than assumed.

- Configuration of existing FairDM and Django behaviour MUST be preferred over new code. A custom implementation
  requires a written reason why configuration cannot serve.
- Abstractions MUST be introduced in response to a present requirement. Speculative generality, unused extension
  points, and indirection added for hypothetical future needs are PROHIBITED.
- New runtime dependencies MUST be justified in the pull request that introduces them, stating what they replace and
  what removing them later would cost.
- Code MUST be readable by a scientist-developer joining the project without prior context: descriptive names, short
  functions, and comments that explain scientific intent rather than restating the code.
- Dead code, commented-out blocks, and unreachable branches MUST be deleted rather than left in place. Version
  control is the archive.
- Where a change adds complexity that cannot be avoided, the reason MUST be recorded in the relevant `plan.md`
  "Complexity Tracking" section.
- Simplicity MUST NOT be bought at the expense of Principles I, II, or VI. Reducing effort by weakening FAIR
  compliance, schema fidelity, or test coverage is not simplification.

### X. Fidelity to the WHDB Project Mission & DFG Funding

The portal is a deliverable of the World Heat Flow Database Project and is built with public research funding from
the DFG (grant 491795283). Work on the portal MUST serve that mission and the scope the project was funded to
deliver.

- Every feature MUST be traceable to the mission of the WHDB Project: a quality-assured, openly available global
  heat flow database serving the international research community.
- The proposals, project descriptions, and reports held in `docs/constitution/references/` are the record of what
  the project committed to deliver. Proposed work outside that commitment MUST state its case before implementation
  begins.
- Obligations attached to the grant MUST be treated as requirements rather than aspirations. The two that bear
  directly on the code are open access to published data releases and a current, accurate data management plan.
- Funding acknowledgement and accurate attribution of the institutional partners (IHFC, GFZ, and contributing
  institutions) MUST appear in public-facing project information and in dataset citation metadata.
- The portal MUST remain usable and maintainable beyond the funded period. Decisions that trade long-term
  stewardship for short-term delivery MUST be documented and revisited.
- Where funded scope and a community request conflict, funded scope takes precedence until project governance
  records a change. The request SHOULD be captured as a future work item rather than dropped or absorbed silently.

---

## Architecture & Stack Constraints

- **Language & Runtime**: Python ≥ 3.13 targeting currently-supported CPython versions per `pyproject.toml`.
- **Web Framework**: Django ≥ 5.0 is the foundational web framework. Alternatives are not permitted without a
  governance-approved decision and migration strategy.
- **Core Dependencies**:
  - FairDM framework (+ `fairdm-geo`, `fairdm-discussions` ecosystem) as the portal backbone.
  - PostgreSQL as the reference and recommended production database.
  - Bootstrap 5 for the responsive, accessible default UI.
  - HTMX and Alpine.js for small, targeted progressive enhancements.
  - Celery + Redis for long-running tasks (import, export, quality score recalculation).
  - Django REST Framework (via FairDM API layer) for programmatic access; generated APIs MUST honour FAIR metadata
    and permission rules.
- **Container-First Deployment**: Docker + docker-compose are the reference deployment strategy; 12-factor-style
  environment variable configuration (via `django-environ`) is REQUIRED.
- **Testing Stack**:
  - pytest and pytest-django are the canonical testing stack.
  - Test organisation: `project/heat_flow/models/foo.py` → `tests/test_heat_flow/test_models/test_foo.py`.
  - Fixtures use factory-boy and pytest fixtures; test isolation uses transaction rollback.
  - Static analysis: Ruff (lint + format), mypy, djlint (HTML templates).
- **Internationalisation Settings**: `USE_I18N = True`, `USE_L10N = True`, and `LANGUAGE_CODE = "en"` are
  non-negotiable defaults in all deployment configurations.
- **Core MUST provide**:
  - Normalised relational storage of all IHFC GHFDB fields per Fuchs et al.
  - Import from and export to the IHFC flat spreadsheet format with round-trip integrity.
  - FAIR-compliant metadata endpoints (DataCite-compatible, machine-readable).
  - Contributor attribution and ORCID/ROR integration.
  - Admin-governed data review and publication workflow.
  - Multilingual UI foundation (i18n-wrapped strings, locale files for `en`).

---

## Development Workflow & Quality Gates

This section governs how changes move from idea to deployed code within the GHFDB Portal project.

- **Specification First**: Non-trivial changes MUST start with a `spec.md` aligned with Principle VIII.
- **Planning & Constitution Check**: Each feature MUST include a `plan.md` with a "Constitution Check" section
  confirming alignment with the Core Principles. Intentional violations MUST be recorded in the
  "Complexity Tracking" table with written justification.
- **Task Breakdown**: Tasks MUST be grouped by user story; shared foundational work MUST be explicit blocking tasks.
- **Test-First**: Tests written and observed failing before implementation, per Principle VI.
- **Implementation Validation Checkpoints**:
  - Run `python manage.py check` after each phase; fix all errors before continuing.
  - Run the full test suite (`poetry run pytest`) before marking any user story complete.
  - Verify FairDM registry integrity after modifying models or `ModelConfig` classes.
  - Update `docs/ghfdb_fields.md` immediately when any schema change is made.
- **Documentation Currency**: Documentation is updated incrementally as capabilities are added, never deferred.
  New public APIs, settings, and mappings MUST be documented before the feature is considered complete.
- **Merge Gates**:
  - All tests MUST pass.
  - Ruff and mypy MUST report no new errors.
  - `python manage.py check` MUST pass with zero errors.
  - Field mapping documentation MUST be current.
  - Relevant docstrings MUST reference Fuchs et al. where the field is IHFC-defined.
- **Workflow Documentation Consistency**: `docs/development/spec-driven-workflow.md` MUST remain consistent with
  this constitution. Divergence MUST be corrected in the same pull request as the constitutional amendment.

---

## Governance

The constitution defines how the GHFDB Portal is evolved and how compliance is enforced.

- **Scope**: This constitution applies to the `ihfc-iugg/ghfdb-portal` repository, all data models, APIs,
  documentation, CI/CD pipelines, and reference deployment configurations maintained here.
- **Authority**: Final authority for constitutional changes and major architectural decisions currently rests with the
  original author acting as BDFL (Benevolent Dictator For Life), while preparing for a broader governance model as
  the project matures within the IHFC community.
- **Amendments & Versioning**:
  - Amendments MUST be made via pull request clearly stating the intended change, rationale, and expected impact.
  - Constitution versions follow semantic versioning:
    - **MAJOR**: Backward-incompatible governance changes; removal or redefinition of existing principles.
    - **MINOR**: Addition of new principles or sections; substantial expansion of existing guidance.
    - **PATCH**: Clarifications, non-semantic wording, and typo fixes.
  - Any change MUST update the version, Last Amended date, and Sync Impact Report at the top of this file.
- **Compliance & Review**:
  - Code review for core changes MUST consider alignment with the Core Principles and Architecture Constraints above.
  - When violations are accepted for pragmatic reasons, they MUST be documented in the relevant `plan.md`
    "Complexity Tracking" section and, where long-lived, reflected as a future constitutional amendment.
  - `AGENTS.md`, `CONTEXT.md`, and the guidance in `docs/agents/` MUST be kept consistent with this constitution.
    Divergence is treated as a documentation bug.
- **Transparency & Community Input**:
  - Proposed constitutional changes SHOULD be discussed openly (via issues or discussions on the repository) before
    being merged.
  - Maintainers SHOULD provide clear, written rationale referencing this document when accepting or rejecting
    significant contributions.
  - As IHFC community members and institutional stakeholders engage more deeply with the project, a formal governance
    structure (e.g., a steering committee aligned with the IHFC working group) SHOULD be established and documented
    as an amendment to this section.

**Version**: 1.1.0 | **Ratified**: TODO(RATIFICATION_DATE): confirm project inception date | **Last Amended**: 2026-08-17
