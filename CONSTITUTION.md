<!-- Rarely changed; amendments land through a dedicated pull request that states the change, the
     reason, and its expected impact, never bundled into a feature change. Read at plan time and
     by reviewers. -->

# Global Heat Flow Database Portal — Constitution

<!-- Standard articles below; keep all unless a repo explicitly strikes one. -->
## Core articles

### Article I — Testing
Every change follows [`docs/contributing/standards/testing.md`](docs/contributing/standards/testing.md): what gets a test
and what does not, the test-first cycle, test structure and fixtures, and the coverage floors.

### Article II — Simplicity
Start with the simplest design that satisfies the spec. New dependencies, new abstractions,
and new infrastructure each require a stated justification in plan.md Complexity Tracking.
YAGNI over speculation.

Configuration of existing FairDM and Django behaviour is preferred over new code; a custom
implementation states why configuration cannot serve. Code is written to be readable by a
scientist-developer joining the project without prior context: descriptive names, short
functions, and comments that explain scientific intent rather than restate the code. Dead code,
commented-out blocks, and unreachable branches are deleted rather than left in place. Simplicity
is never bought at the expense of FAIR compliance (Article XI), schema fidelity (Article XII), or
test coverage (Article I).

### Article III — Anti-Abstraction
No wrapper layers, base classes, or "future-proofing" indirection without a present, concrete
second use. Prefer duplication over the wrong abstraction.

### Article IV — Integration-First
Contracts and integration points are designed and tested before internals are polished.
Acceptance scenarios exercise the system the way users touch it.

### Article V — Security & data-safety
Values interpolated into rendered output are escaped through the framework's template layer,
never hand-built string interpolation of model or user data. Secrets live in runtime config,
never in code, fixtures, or version control. Authentication, authorisation, cryptography and
permission changes never take a shortened review path.

### Article VI — Documentation
Public API changes ship their docs in the same PR: README + CHANGELOG updated. Docstrings,
component annotations and code comments follow
[`docs/contributing/standards/code-documentation.md`](docs/contributing/standards/code-documentation.md). If the repo ships
built docs, they must build clean.

Every public model field, setting, API endpoint, and schema mapping is documented with a
reference to the relevant IHFC specification section (Fuchs et al., 2021, 2023) where applicable.
The field mapping table (`docs/ghfdb_fields.md`) is updated in the same pull request as any schema
change. New public settings, template blocks, and public APIs include at least one minimal usage
example in the docs. Breaking changes include migration guides with step-by-step upgrade
instructions. Documentation is versioned alongside code releases.

### Article VII — Dependency discipline
A new runtime dependency requires a stated justification (Simplicity applied to the dependency
tree; prefer the shared `mvp-shared` toolchain bundle over ad-hoc dev deps). `deptry` must pass:
no unused, missing, or transitively-relied-upon dependencies.

### Article VIII — Internationalization
User-facing strings are translatable. In Python (models, forms, views, admin, template tags,
validators) they are wrapped with `gettext_lazy` (imported as `_`); templates load
`{% load i18n %}` and wrap strings with `{% trans %}` / `{% blocktrans %}`. Model `verbose_name`
/ `verbose_name_plural` and form `label` / `help_text` / `error_messages` use `gettext_lazy`; pure
acronyms are exempt. No hard-coded natural-language string (error message, label, help text,
button label) ships outside a translation wrapper — this has zero exceptions for user-visible
strings.

Translation files (`.po`/`.mo`) are maintained in the repository, with English (`en`) as the
baseline; additional languages may be contributed by the community. CI runs `makemessages` clean
over the source as the i18n gate; correct wrapper usage is otherwise enforced by review, and a
hard-coded user-visible string in a PR is a blocking comment.

Accessibility (WCAG 2.1 AA) is treated alongside internationalisation as a non-optional quality
dimension: regressions in keyboard navigation, contrast ratios, or semantic HTML are treated as
bugs.

### Article IX — Data-model conventions (Django)
Every model field is a deliberate indexing decision. Because consumers of a published package cannot
add their own indexes, any field with a plausible lookup / filter / ordering path is indexed at its
definition (`db_index`, `unique`, an FK's automatic index, or a composite `Meta.constraints` /
`Meta.indexes`); a field with no query path stays unindexed to avoid write cost. The choice —
indexed or not, and why — is recorded (plan `data-model.md` or `decisions.md`). `verbose_name` and
`help_text` are mandatory on every model field (Article VIII). **Migrations are consolidated per
PR:** the migrations a feature branch introduces are squashed into as few files as possible before
the PR is submitted (branch-local and unapplied, so safe at any release stage); data migrations
(`RunPython`/`RunSQL`) are exempt from auto-regeneration — keep them via `squashmigrations` or
standalone.

### Article X — Cohesion (Python)
Related behaviour is grouped in a class, not scattered across module-level functions.

**The test:** two or more module-level functions that share a *subject* belong on a class. They
share a subject when they operate on the same data, take the same first argument, are only
meaningful in sequence, or are named around the same noun (`build_x`, `validate_x`, `render_x`).

**Why this is a standard and not a taste.** In a published package, a class is the extension
point. A consumer who needs different behaviour subclasses it and overrides one method. A module
of functions can only be monkey-patched, which is not a supported interface and breaks on any
internal change. Grouping also gives the behaviour a name, a place for shared configuration, and
one import instead of six.

**Shape:** shared state or configuration → a regular class holding it. Grouping for namespacing
with no shared state → still a class, with `@classmethod`/`@staticmethod`, or a small frozen
dataclass carrying the config. Expose a module-level convenience function only as a thin wrapper
over the class, never as the implementation.

**Django first.** Where the framework already owns the grouping, use it rather than inventing a
class: a `QuerySet`/`Manager` method instead of a function taking a queryset, a model method or
property instead of a function taking an instance, a `Form`/`Serializer` method instead of a free
validation function, a `TemplateView` method instead of a helper called by a view.

**Exceptions — narrow, and stated rather than assumed.** A genuinely standalone pure function with
no siblings. Framework-dictated module shapes: `conftest.py` fixtures, migrations, `urls.py`,
`apps.py`, decorator-registered template tags and filters, signal receivers, management-command
entry points. Factory functions that return the class. A module of independent utilities that
genuinely share no subject.

**This does not license abstraction.** Article III still holds: one class grouping today's
behaviour is the goal, not a base class, a registry, or a hierarchy built for a second
implementation that does not exist. Grouping related functions is organisation; adding a layer
between the caller and the work is not.

<!-- Each project article is a rule a reviewer can check against any change: what code may or may
     not do. What the portal is for, the stance it takes, and why, belong in the README's Scope &
     philosophy section, GOALS.md or an ADR. An article that reads as a direction is a goal in the
     wrong file. -->
## Project articles (GHFDB Portal-specific)

### Article XI — FAIR-First Scientific Data

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

### Article XII — GHFDB Schema Fidelity & Domain Integrity

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
- All scientific units displayed in the UI MUST be labelled unambiguously; where SI and non-SI variants exist, the
  canonical IHFC unit convention (as defined in Fuchs et al.) MUST be used with clear labelling.

### Article XIII — FairDM-First Integration

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

### Article XIV — Open Science, Provenance & Review Governance

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

### Article XV — Spec-Driven Development Workflow

All non-trivial changes MUST follow the spec-driven workflow documented in
`docs/development/spec-driven-development.md`, producing discoverable, version-controlled design artefacts.

- Non-trivial changes MUST start with a feature specification (`spec.md`) that articulates user stories, priorities,
  and measurable success criteria in scientific and user-journey terms.
- User stories MUST be independently testable slices of value, ordered by priority (P1, P2, P3, …).
- Each feature MUST include an implementation plan (`plan.md`) recording technical context, chosen architecture, and
  a "Constitution Check" section that explicitly notes alignment with the constitution's articles above.
- Tasks (`tasks.md`) MUST be grouped by user story to enable independent implementation, testing, and delivery.
- **Django System Checks**: `python manage.py check` MUST pass between completing user stories or major
  implementation phases. All system check errors MUST be fixed before proceeding.
- **Validation Frequency**: For multi-phase implementations, run system checks after each phase; test FairDM
  registry integration immediately after modifying models or configuration classes.
- Documentation MUST be updated as features are implemented, not deferred to the end.

### Article XVI — Fidelity to the WHDB Project Mission & DFG Funding

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

- **Specification First**: Non-trivial changes MUST start with a `spec.md` aligned with Article XV.
- **Planning & Constitution Check**: Each feature MUST include a `plan.md` with a "Constitution Check" section
  confirming alignment with the Core and Project articles. Intentional violations MUST be recorded in the
  "Complexity Tracking" table with written justification.
- **Task Breakdown**: Tasks MUST be grouped by user story; shared foundational work MUST be explicit blocking tasks.
- **Test-First**: Tests written and observed failing before implementation, per Article I.
- **Implementation Validation Checkpoints**:
  - Run `python manage.py check` after each phase; fix all errors before continuing.
  - Run the full test suite (`uv run pytest`) before marking any user story complete.
  - Verify FairDM registry integrity after modifying models or `ModelConfig` classes.
  - Update `docs/ghfdb_fields.md` immediately when any schema change is made.
- **Documentation Currency**: Documentation is updated incrementally as capabilities are added, never deferred.
  New public APIs, settings, and mappings MUST be documented before the feature is considered complete.
- **Merge Gates**:
  - All tests MUST pass.
  - Ruff and mypy MUST report no new errors.
  - `deptry` MUST report no unused, missing, or transitively-relied-upon dependencies.
  - `python manage.py check` MUST pass with zero errors.
  - Coverage meets the floors in `docs/contributing/standards/testing.md` (`codecov.yml` is the enforcement
    reference).
  - Field mapping documentation MUST be current.
  - Relevant docstrings MUST reference Fuchs et al. where the field is IHFC-defined.
- **Workflow Documentation Consistency**: `docs/development/spec-driven-development.md` MUST remain consistent with
  this constitution. Divergence MUST be corrected in the same pull request as the constitutional amendment.

## Non-negotiables

- Tests, build and lint pass before a change merges. Nobody overrides a red check.
- The default branch requires one approval, and the author of a change never approves it.

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
    - **MAJOR**: Backward-incompatible governance changes; removal or redefinition of existing articles.
    - **MINOR**: Addition of new articles or sections; substantial expansion of existing guidance.
    - **PATCH**: Clarifications, non-semantic wording, and typo fixes.
  - Any change MUST update the version and Last Amended date at the foot of this file.
- **Compliance & Review**:
  - Code review for core changes MUST consider alignment with the Core and Project articles and Architecture
    Constraints above.
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

<!-- The footer below is mandatory and closes every constitution, so a review can name the
     revision it was made against. Format is fixed: bold labels with the colon outside the
     bold, ISO dates, "Last Amended" capitalized, last line of the file. Versioning is
     semantic — MAJOR for a removed or redefined article, MINOR for a new article or
     materially expanded guidance, PATCH for clarification and wording. -->

---

**Version**: 2.0.0 | **Ratified**: TODO(RATIFICATION_DATE): confirm project inception date | **Last Amended**: 2026-09-28
