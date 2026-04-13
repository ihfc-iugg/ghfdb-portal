# Implementation Plan: GHFDB Product Layer — Import/Export Resources

**Branch**: `002-ghfdb-product-utilities` | **Date**: 2026-04-13 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-ghfdb-product-utilities/spec.md`

**Replanning Note**: This plan is written from scratch. The existing `project/ghfdb/resources.py` was a prior manual attempt with minimal planning and is **not** the basis for this design. All import/export resource architecture is designed fresh using spec-driven principles.

## Summary

The GHFDB product layer treats the Global Heat Flow Database as a first-class import/export product within the Django portal. This plan covers: (1) a GHFDB proxy model over `HeatFlow` with optimised flat-query methods, (2) **separate** import resources for parent-level and child-level data using custom `RelatedModelWidget` classes that create/update related models from flat spreadsheet columns with field-level error reporting, (3) an export resource that serialises the normalised relational model back to the flat GHFDB spreadsheet format, and (4) a map viewer page. The import architecture uses a two-resource split (parent import → child import) for independent testability, faster per-resource processing, and the ability to update parent records without touching child data.

## Technical Context

**Language/Version**: Python ≥3.13
**Primary Dependencies**: Django 5.0+, FairDM framework, django-import-export ≥4.0.3 <5.0.0, research-vocabs, django-pint-field, openpyxl, tablib
**Storage**: PostgreSQL (reference); SQLite for local dev
**Testing**: pytest + pytest-django, factory-boy
**Target Platform**: Linux server (Docker), Windows dev
**Project Type**: Web application (Django portal)
**Performance Goals**: Import 10,000-row GHFDB spreadsheet with full validation in <60 seconds; constant query count for `as_ghfdb_flat()`
**Constraints**: Synchronous processing acceptable for files ≤50,000 rows / 20 MB; staff-only admin access for import/export
**Scale/Scope**: ~60 GHFDB spreadsheet columns, 6 relational models in the import graph, 14 M2M relations for export

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify alignment with the [GHFDB Portal Constitution](../../.specify/memory/constitution.md) before proceeding:

| Principle | Question | Status |
|-----------|----------|--------|
| I. FAIR-First | Does this feature improve or maintain FAIR characteristics? Are identifiers (DOI/ORCID/IGSN) preserved? | [x] Import/export enables FAIR data exchange. `local_id` (GHFDB ID) and IGSNs are preserved through round-trip. DOI/ORCID not directly in spreadsheet scope but not degraded. |
| II. GHFDB Schema Fidelity | Does this touch GHFDB models? If so, is `docs/ghfdb_fields.md` updated? Are Fuchs et al. references in docstrings? | [x] Uses existing models without schema changes. Field mapping table already current. All import/export field mappings reference `docs/ghfdb_fields.md`. Docstrings will cite Fuchs et al. |
| III. FairDM-First | Is this implemented via FairDM base classes and registry? Is custom re-implementation avoided? | [x] GHFDB proxy extends `HeatFlow` (FairDM `Measurement`). No FairDM-provided import/export exists, so custom resources are justified. Proxy is NOT registered with FairDM registry (admin-only). |
| IV. Open Science & Provenance | Does this respect the review/approval workflow? Is contributor attribution preserved? | [x] Import/export is staff-only admin action. Imported data enters as unpublished; review workflow is out of scope but not bypassed. Contributor fields preserved in round-trip. |
| V. Internationalisation | Are all new user-facing strings wrapped in `_()` / `gettext_lazy()`? Dates/numbers using locale utilities? | [x] Admin labels, error messages, and verbose names will use `gettext_lazy`. Export uses SI units per Fuchs et al. convention (not locale-dependent). |
| VI. Test-First Quality | Are tests written first (TDD)? Do schema-mapping or score calculations have pinned regression tests? | [x] Round-trip import/export tests with known GHFDB sample data will be pinned regression tests. Each resource tested independently. Query-count assertions for proxy model. |
| VII. Documentation | Is `docs/ghfdb_fields.md` current? Are new settings/APIs documented with examples? | [x] No new fields added. Import/export column mapping documented via `ghfdb_colmeta.json` and `docs/ghfdb_fields.md`. Quickstart guide produced. |
| VIII. Spec-Driven Workflow | Does this feature follow spec.md → plan.md → tasks.md workflow? Are users stories prioritised? | [x] Following spec.md → plan.md → tasks.md. User stories ordered P1 (proxy) → P2 (import, export) → P3 (map viewer). |

## Project Structure

### Documentation (this feature)

```text
specs/002-ghfdb-product-utilities/
├── plan.md              # This file
├── research.md          # Phase 0 output — architecture decisions
├── data-model.md        # Phase 1 output — resource class design
├── quickstart.md        # Phase 1 output — developer setup guide
├── contracts/           # Phase 1 output — import/export column contracts
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
project/
├── ghfdb/
│   ├── models.py            # GHFDB proxy model, GHFDBRelease (existing)
│   ├── managers.py          # GHFDBQuerySet.as_ghfdb_flat(), .for_export() (existing)
│   ├── admin.py             # GHFDBAdmin with ImportExportMixin (modify)
│   ├── resources/
│   │   ├── __init__.py      # Public re-exports
│   │   ├── _base.py         # Shared constants, column order, format class
│   │   ├── _widgets.py      # ConceptWidget, MultiConceptWidget, QuantityWidget, YesNoWidget
│   │   ├── parent.py        # GHFDBParentImportResource
│   │   ├── child.py         # GHFDBChildImportResource
│   │   └── export.py        # GHFDBExportResource
│   ├── views.py             # GHFDBExploreView (existing, extend)
│   ├── urls.py              # explore/ URL (existing, extend)
│   ├── templates/
│   │   └── ghfdb/
│   │       └── explore.html # Map viewer template
│   └── data/
│       └── ghfdb_colmeta.json  # Column metadata (existing)
├── heat_flow/
│   └── models/              # No changes — existing models used as-is
└── ...

tests/
├── test_ghfdb/
│   ├── test_resources/
│   │   ├── test_widgets.py       # Unit tests for custom widgets
│   │   ├── test_parent_import.py # Parent resource import tests
│   │   ├── test_child_import.py  # Child resource import tests
│   │   ├── test_export.py        # Export resource tests
│   │   └── test_roundtrip.py     # End-to-end round-trip regression tests
│   ├── test_models.py           # Proxy model / queryset tests
│   └── test_views.py            # Map viewer view tests
└── ...
```

**Structure Decision**: The import resources are split into a `resources/` package within `project/ghfdb/` to cleanly separate parent import, child import, export, shared widgets, and base constants. This replaces the monolithic `resources.py` file. Tests mirror this structure under `tests/test_ghfdb/test_resources/`.

## Constitution Re-Check (Post Phase 1 Design)

*Re-evaluation after data-model.md, contracts/, and quickstart.md are complete.*

| Principle | Post-Design Status |
|-----------|-------------------|
| I. FAIR-First | **PASS** — Import preserves `local_id` (GHFDB identifier) for both parent and child. Export produces the IHFC-canonical flat format. No identifier degradation. |
| II. GHFDB Schema Fidelity | **PASS** — All 60+ GHFDB columns mapped in contracts. Field mapping tables in contracts reference `docs/ghfdb_fields.md`. No schema divergence; all data stored at correct hierarchy level (site vs interval vs child). Corrections stored as separate `HeatFlowCorrection` records per Fuchs et al. |
| III. FairDM-First | **PASS** — Resources use existing FairDM-derived models without modification. Custom resources justified: FairDM provides no GHFDB-specific import/export. Proxy model extends `HeatFlow` (FairDM `Measurement`). |
| IV. Open Science & Provenance | **PASS** — Import is staff-only admin action; data enters as unpublished (review workflow not bypassed). Export respects queryset filters. Contributor attribution fields preserved. |
| V. Internationalisation | **PASS** — Widget error messages, admin labels, and verbose names will use `gettext_lazy`. `ConceptWidget` uses vocabulary labels (language-neutral URIs beneath). Export uses canonical IHFC units. |
| VI. Test-First Quality | **PASS** — Test structure defined: `test_widgets.py`, `test_site_import.py`, `test_child_import.py`, `test_export.py`, `test_roundtrip.py`. Round-trip regression tests with known data pinned. Query-count assertions planned. |
| VII. Documentation | **PASS** — Import/export contracts fully document column mappings. `quickstart.md` provides developer guide. `docs/ghfdb_fields.md` already current (no new model fields added). |
| VIII. Spec-Driven Workflow | **PASS** — Following spec.md → plan.md → tasks.md. Artifacts produced: research.md, data-model.md, contracts/, quickstart.md. |

**Result**: All 8 principles pass. No violations or waivers required.

## Complexity Tracking

> No constitution violations requiring justification. Custom import/export resources are necessary because FairDM does not provide GHFDB-specific import/export functionality (Principle III exemption documented above).
