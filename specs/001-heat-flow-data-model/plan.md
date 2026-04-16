# Implementation Plan: GHFDB Normalized Relational Data Model

**Branch**: `001-heat-flow-data-model` | **Date**: 2026-04-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-heat-flow-data-model/spec.md`

## Summary

Define and implement the normalized relational data model for the GHFDB portal, capturing the full IHFC parent/child hierarchy (site → interval → child measurement) as Django models that extend FairDM `Sample` and `Measurement` base classes. Register primary models with the FairDM registry, create factory-boy factories for all models, and write comprehensive tests for persistence, relationships, constraints, and registration. All fields use plain-language names; GHFDB-mandatory fields are nullable at the DB level (enforced programmatically at export/validation time). Round-trip import/export and quality-score algorithms are deferred.

## Technical Context

**Language/Version**: Python ≥3.13
**Primary Dependencies**: Django 5.0+, FairDM (`fairdm`, `fairdm-geo`), `research_vocabs`, `django-pint` (via `fairdm.db.fields`), `django-polymorphic`, `factory_boy`
**Storage**: SQLite (development), PostgreSQL + PostGIS (production)
**Testing**: pytest + pytest-django, factory_boy fixtures
**Target Platform**: Linux server (Docker), development on Windows
**Project Type**: Web application (FairDM portal)
**Performance Goals**: N/A for this spec (data model layer only)
**Constraints**: All GHFDB-mandatory fields nullable at DB level **except primary `value` fields**, which are non-nullable (`null=False`) per R3 — applies to `HeatFlow.value`, `ThermalGradient.value`, and `IntervalConductivity.value` (spec clarification 2026-04-10); all remaining GHFDB-mandatory fields default to nullable, with validation enforced at application/export boundary only
**Scale/Scope**: 8 model classes, 4 FairDM registrations, 7+ factories, ~150-200 test assertions

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify alignment with the [GHFDB Portal Constitution](.specify/memory/constitution.md) before proceeding:

| Principle | Question | Status |
|-----------|----------|--------|
| I. FAIR-First | Does this feature improve or maintain FAIR characteristics? Are identifiers (DOI/ORCID/IGSN) preserved? | [x] Yes — `IGSN` removed from `HeatFlow` per spec clarification 2026-04-10 (C49/IGSN is served by FairDM's Sample identifier relationship on `HeatFlowSite`/`HeatFlowInterval`); models extend FairDM which provides DOI/ORCID infrastructure; PID fields are first-class via FairDM backbone (L2). |
| II. GHFDB Schema Fidelity | Does this touch GHFDB models? If so, is `docs/ghfdb_fields.md` updated? Are Fuchs et al. references in docstrings? | [x] Yes — all P01–P13 and C01–C49 IHFC fields are mapped to Django model fields. `docs/ghfdb_fields.md` update is a task requirement. Docstrings will reference Fuchs et al. |
| III. FairDM-First | Is this implemented via FairDM base classes and registry? Is custom re-implementation avoided? | [x] Yes — HeatFlowSite/HeatFlowInterval extend Sample (via fairdm-geo); ParentHeatFlow/HeatFlow/ThermalGradient/IntervalConductivity extend Measurement. All four primary models registered via `@fairdm.register`. |
| IV. Open Science & Provenance | Does this respect the review/approval workflow? Is contributor attribution preserved? | [x] Yes — review/approval workflow is inherited from FairDM Dataset; contributor attribution via GenericRelation to Contribution model. No custom overrides. |
| V. Internationalisation | Are all new user-facing strings wrapped in `_()` / `gettext_lazy()`? Dates/numbers using locale utilities? | [x] Yes — all `verbose_name`, `help_text`, and choice labels will use `gettext_lazy`. |
| VI. Test-First Quality | Are tests written first (TDD)? Do schema-mapping or score calculations have pinned regression tests? | [x] Yes — US5 mandates factories; US1-4 each have independent test criteria. TDD cycle required by constitution. Score calculation tests deferred (algorithm is out of scope). |
| VII. Documentation | Is `docs/ghfdb_fields.md` current? Are new settings/APIs documented with examples? | [x] Yes — field mapping table update is an explicit task. Model docstrings reference Fuchs et al. |
| VIII. Spec-Driven Workflow | Does this feature follow spec.md → plan.md → tasks.md workflow? Are users stories prioritised? | [x] Yes — spec.md complete with P1–P5 user stories; this is plan.md; tasks.md follows. |

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
project/
└── heat_flow/
    ├── __init__.py
    ├── apps.py
    ├── config.py              # FairDM registry configuration (ModelConfiguration subclasses)
    ├── vocabularies.py        # VocabularyBuilder definitions for GHFDB controlled terms
    ├── factories.py           # factory_boy factories for all models
    ├── filters.py             # django-filter filtersets
    ├── tables.py              # django-tables2 table classes
    ├── models/
    │   ├── __init__.py        # Re-exports all model classes
    │   ├── parent.py          # HeatFlowSite (Sample), ParentHeatFlow (Measurement)
    │   └── child.py           # HeatFlowInterval (Sample), HeatFlow (Measurement),
    │                          # ThermalGradient (Measurement), IntervalConductivity (Measurement),
    │                          # ProbeMetadata (Model), HeatFlowCorrection (Model)
    └── migrations/

tests/
└── test_heat_flow/
    ├── __init__.py
    ├── conftest.py            # Shared fixtures (factories, sample instances)
    ├── test_models.py         # Model persistence, relationships, constraints, save() validation
    ├── test_factories.py      # Factory smoke tests
    └── test_config.py         # FairDM registry integration tests
```

**Structure Decision**: Follows existing Django app layout under `project/heat_flow/`. Models split into `parent.py` (site-level: HeatFlowSite, ParentHeatFlow) and `child.py` (interval-level: HeatFlowInterval plus all child measurements). Tests mirror the app under `tests/test_heat_flow/`. No new apps or packages are introduced.

## Complexity Tracking

> No constitution violations identified. All 8 principles pass.
