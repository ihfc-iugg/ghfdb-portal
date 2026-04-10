# Implementation Plan: GHFDB Product Layer

**Branch**: `002-ghfdb-product-utilities` | **Date**: 2026-04-10 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-ghfdb-product-utilities/spec.md`

## Summary

This feature establishes the GHFDB as a first-class product layer within the portal by adding: (1) a `GHFDB` proxy model over `HeatFlow` with an optimised flat queryset that mirrors the GHFDB spreadsheet schema (one row per child measurement, all parent/site/gradient/conductivity columns inlined); (2) round-trip XLSX import/export utilities using django-import-export, triggered exclusively from the Django admin, that convert between the flat GHFDB spreadsheet and the normalised relational model; and (3) a full-screen "Explore" map page embedding the IHFC web-map viewer. The existing `project/ghfdb/resources.py` already contains substantial import logic (field mapping, vocabulary widgets, foreign-object creation) which will be refactored and extended rather than rewritten.

## Technical Context

**Language/Version**: Python ≥3.13 (CPython)
**Primary Dependencies**: Django 5.0+, FairDM framework, django-import-export (via FairDM), django-pint (Quantity fields), research-vocabs (Concept/vocabulary fields), openpyxl (XLSX read/write), tablib, django-flex-menu
**Storage**: PostgreSQL (production); SQLite (development/CI)
**Testing**: pytest + pytest-django, factory-boy fixtures
**Target Platform**: Linux Docker containers (production); Windows dev
**Project Type**: Django web application (research data portal)
**Performance Goals**: Constant-count DB queries for `as_ghfdb_flat()` regardless of row count (no N+1); 10,000-row import with full validation report within 60 seconds
**Constraints**: Synchronous in-request processing acceptable up to ~50,000 rows / 20 MB; larger imports deferred to future background-task spec
**Scale/Scope**: ~80,000 existing GHFDB records; ~65 GHFDB spreadsheet columns; single Django admin interface for import/export

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify alignment with the [GHFDB Portal Constitution](../../.specify/memory/constitution.md) before proceeding:

| Principle | Question | Status |
|-----------|----------|--------|
| I. FAIR-First | Does this feature improve or maintain FAIR characteristics? Are identifiers (DOI/ORCID/IGSN) preserved? | ✅ Yes — the proxy model and export utility make GHFDB data more Findable and Interoperable by providing a standardised flat output matching the community-defined schema. Import preserves contributor attribution and literature references. No identifiers are discarded. |
| II. GHFDB Schema Fidelity | Does this touch GHFDB models? If so, is `docs/ghfdb_fields.md` updated? Are Fuchs et al. references in docstrings? | ✅ Yes — the proxy model reads from the existing normalised model without adding tables. All 65 GHFDB columns from `ghfdb_colmeta.json` and `ghfdb_fields.md` must be covered. Docstrings will cite Fuchs et al. (2021, 2023). `ghfdb_fields.md` will be updated to document the proxy model access patterns. |
| III. FairDM-First | Is this implemented via FairDM base classes and registry? Is custom re-implementation avoided? | ✅ Yes — the proxy model delegates to `HeatFlow` (a `Measurement` subclass). Import/export uses django-import-export via FairDM's admin integration. No FairDM-provided functionality is reimplemented. The existing `GHFDBResource` class is extended rather than replaced. |
| IV. Open Science & Provenance | Does this respect the review/approval workflow? Is contributor attribution preserved? | ✅ Yes — import creates Review records and preserves reviewer attribution. Export is admin-only (staff). No data is published without the existing review workflow. |
| V. Internationalisation | Are all new user-facing strings wrapped in `_()` / `gettext_lazy()`? Dates/numbers using locale utilities? | ✅ Will comply — all new model verbose_names, help_texts, admin labels, and template strings will be wrapped in translation utilities. The existing codebase already follows this pattern. |
| VI. Test-First Quality | Are tests written first (TDD)? Do schema-mapping or score calculations have pinned regression tests? | ✅ Will comply — round-trip import/export tests with known inputs will be the primary acceptance tests. Proxy queryset will have query-count assertions. All tests written before implementation per constitution. |
| VII. Documentation | Is `docs/ghfdb_fields.md` current? Are new settings/APIs documented with examples? | ✅ Will comply — `ghfdb_fields.md` will be updated to document the GHFDB proxy model access patterns. The admin import/export workflow will be documented. |
| VIII. Spec-Driven Workflow | Does this feature follow spec.md → plan.md → tasks.md workflow? Are users stories prioritised? | ✅ Yes — this plan follows the spec-driven workflow. User stories are prioritised P1→P3. |

## Project Structure

### Documentation (this feature)

```text
specs/002-ghfdb-product-utilities/
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
├── ghfdb/
│   ├── __init__.py
│   ├── models.py           # GHFDBRelease (existing) + GHFDB proxy model (NEW)
│   ├── managers.py          # GHFDBQuerySet + GHFDBManager (NEW)
│   ├── resources.py         # GHFDBResource (existing, refactored) + GHFDBExportResource (NEW)
│   ├── admin.py             # GHFDBAdmin read-only + import/export admin actions (NEW)
│   ├── forms.py             # GHFDBImportForm (existing)
│   ├── views.py             # GHFDBExploreView (existing)
│   ├── urls.py              # explore URL (existing)
│   ├── serializers.py       # API serializer (existing)
│   ├── templates/
│   │   └── ghfdb/
│   │       └── explore.html # Map viewer template (existing)
│   └── data/
│       └── ghfdb_colmeta.json  # Column metadata (existing, reference)
├── heat_flow/
│   ├── models/              # HeatFlowSite, ParentHeatFlow, HeatFlow, etc. (existing, unchanged)
│   ├── menus.py             # Explore menu item (existing)
│   └── ...
└── ...

tests/
├── test_ghfdb/              # NEW test directory
│   ├── __init__.py
│   ├── conftest.py          # Fixtures for GHFDB-specific tests
│   ├── test_models.py       # GHFDB proxy model tests
│   ├── test_managers.py     # Queryset / as_ghfdb_flat() tests + query-count guards
│   ├── test_import.py       # Import resource tests (round-trip, validation, upsert)
│   ├── test_export.py       # Export resource tests (column order, multi-value, units)
│   └── test_admin.py        # Admin integration tests
└── test_heat_flow/          # Existing tests (unchanged)
    └── ...

docs/
├── ghfdb_fields.md          # Updated with proxy model access patterns
└── ...
```

**Structure Decision**: The `project/ghfdb/` app is the natural home for all GHFDB-product-layer code. The proxy model, import/export resources, and admin classes all belong here. No new Django apps are needed. Tests go in a new `tests/test_ghfdb/` directory mirroring the source structure.

## Complexity Tracking

No constitution violations identified. All eight principles are satisfied by the design. No complexity justifications needed.

## Post-Design Constitution Re-Check

After completing Phase 0 research and Phase 1 design, all principles re-verified:

| Principle | Post-Design Status |
|---|---|
| I. FAIR-First | ✅ Confirmed — proxy model + export produce community-standard GHFDB format. Import preserves all identifiers and attribution. |
| II. GHFDB Schema Fidelity | ✅ Confirmed — data-model.md maps all 65 GHFDB columns. One new field (`HeatFlow.local_id`) added for upsert; documented in data-model.md. `ghfdb_fields.md` update is a task deliverable. |
| III. FairDM-First | ✅ Confirmed — proxy delegates to `HeatFlow(Measurement)`. No FairDM reimplementation. django-import-export used via admin mixin. |
| IV. Open Science & Provenance | ✅ Confirmed — import preserves Review records, reviewer names, literature references. Export is staff-only. |
| V. Internationalisation | ✅ Confirmed — all new strings will use `gettext_lazy()` per existing codebase convention. Research confirmed no hard-coded strings in the design. |
| VI. Test-First Quality | ✅ Confirmed — research.md specifies query-count guards, round-trip regression tests, column completeness tests. TDD approach mandated. |
| VII. Documentation | ✅ Confirmed — `ghfdb_fields.md` update, admin workflow docs, and quickstart.md all planned as deliverables. |
| VIII. Spec-Driven Workflow | ✅ Confirmed — spec.md → plan.md → research.md → data-model.md → contracts → quickstart.md produced. tasks.md is the next step. |
