# Feature Specification: GHFDB Import/Export Pipeline

**Feature Branch**: `003-ghfdb-import-export`
**Created**: 2026-04-15 (split from `002-ghfdb-product-utilities`)
**Status**: Complete
**Dependency**: Requires `002-ghfdb-product-utilities` — GHFDB proxy model, `GHFDBManager.for_export()`, and `local_id` fields on `HeatFlow`, `HeatFlowSite`, and `ParentHeatFlow`.
**Refined**: 2026-04-15 — Added controlled-vocabulary import normalization for bracket-wrapped and mixed-case template values.
**Bugfix**: 2026-04-14 — [BUG-002] Added admin import-route compatibility requirement for django-import-export hook methods.
**Bugfix**: 2026-04-14 — [BUG-003] Updated import upsert identifiers for standard upload templates that omit `ID`/`ID_parent`.
**Bugfix**: 2026-04-15 — [BUG-003] Clarified header-validation-safe upsert: template fallback MUST work when `ID` / `ID_parent` headers are absent from uploaded files.
**Bugfix**: 2026-04-15 — [BUG-004] Documented correct GHFDB template row structure: row 7 = unit labels, row 8 = "Allowed range of values" (both skipped); data rows begin at row 9.
**Bugfix**: 2026-04-15 — [BUG-005] Added confirm-page display constraint: the internal `AUTO_PARENT:` / `AUTO_CHILD:` synthetic upsert keys must never appear in the user-facing import confirm-page diff view; `ID_parent` must show the actual `ParentHeatFlow.local_id` value (or be empty for standard uploads with no explicit ID).
**Bugfix**: 2026-04-15 — [BUG-006] Added confirm-page column-order constraint: the import confirm-page diff view MUST present columns in the same left-to-right order as the GHFDB spreadsheet template (`PARENT_COLUMNS` for the parent resource; `GHFDB_COLUMN_ORDER` for the child resource).
**Bugfix**: 2026-04-16 — [BUG-007] Added widget type-guard requirement: all widget `clean()` methods that call `.strip()` (directly or via `CharWidget`) MUST wrap that call in `try/except AttributeError` and re-raise as a descriptive `ValueError` naming the column and the unexpected value, so that numeric cell values from the XLSX loader produce actionable errors rather than a bare `AttributeError`.
**Bugfix**: 2026-04-16 — [BUG-008] Scoped BUG-007 type-guard to **text-type sentinel columns only**: `RelatedModelWidget.clean()` sentinel check MUST treat a numeric (`int`/`float`) sentinel value as **present** and proceed rather than raising `ValueError`; the error-on-numeric guard applies only to widgets whose sentinel column holds vocabulary text (e.g. `name` on `ParentWidget`). Updated Acceptance Scenario 8 accordingly and added Scenario 9 for valid numeric quantity import.
**Bugfix**: 2026-04-16 — [BUG-009] Clarified `geo_stratigraphy` target field: `IntervalWidget.m2m_map` MUST map `geo_stratigraphy` to `HeatFlowInterval.age` (a `ConceptManyToManyField(vocabulary=GeologicalTimescale)`) — NOT `HeatFlowInterval.stratigraphy`, which is a separate `ManyToManyField(to="stratigraphy.StratigraphicUnit")` and cannot accept `Concept` objects. Added Acceptance Scenario 10.
**References**: Fuchs et al. (2021); Fuchs et al. (2023); IHFC GHFDB v2024
**Split from**: `002-ghfdb-product-utilities` — User Stories 2 & 3

## Overview

This feature implements the GHFDB round-trip import/export pipeline within the `project/ghfdb` app. A `resources/` package provides:

1. **Parent import resource** (`GHFDBParentImportResource`) — ingests parent-level site records from an official GHFDB XLSX spreadsheet into `HeatFlowSite`, `ParentHeatFlow`, and supporting models.
2. **Child import resource** (`GHFDBChildImportResource`) — ingests child heat-flow measurements and all sub-records (`HeatFlow`, `HeatFlowInterval`, `ThermalGradient`, `IntervalConductivity`, `HeatFlowCorrection`, `ProbeMetadata`).
3. **Export resource** (`GHFDBExportResource`) — serialises the normalised database back to the flat GHFDB spreadsheet format using the `GHFDB` proxy model's `for_export()` queryset (from `002-ghfdb-product-utilities`).

All import/export actions are staff-only via the Django admin. Vocabulary tokens from spreadsheet cells are normalised (square brackets stripped, then lowercased) before matching database concepts (FR-016), ensuring standard GHFDB upload-template values such as `[Onshore (continental)]` are accepted.

**Out of scope**: Scheduled/automated release generation; public/anonymous downloads. These remain deferred to a separate feature.

---

## User Scenarios & Testing *(mandatory)*

### User Story 2 - Import GHFDB Spreadsheet into Heat Flow Data Model (Priority: P2)

A data manager has a GHFDB-format XLSX file exported from the official IHFC spreadsheet template. They want to ingest it into the application's normalised heat_flow data model without manually mapping every column.

**Why this priority**: Ingesting official GHFDB releases is the primary data-loading workflow. The existing `resources.py` contains partial import logic; this story formalises and completes it as a first-class utility.

**Independent Test**: Can be tested by providing a sample GHFDB spreadsheet and confirming that the resulting database records match the spreadsheet rows exactly, including controlled-vocabulary mappings and multi-value semicolon-separated fields.

**Acceptance Scenarios**:

1. **Given** a valid GHFDB XLSX file, **When** the import utility is run, **Then** `HeatFlow`, `HeatFlowSite`, `ParentHeatFlow`, `ThermalGradient`, and `IntervalConductivity` records are created with correct field mappings.
2. **Given** a spreadsheet row containing semicolon-separated controlled-vocabulary values (e.g., `q_method`, `tc_method`) where one or more values may be wrapped in square brackets and/or provided with mixed casing, **When** the importer processes it, **Then** each vocabulary token is normalised by removing `[` and `]` and converting to lowercase before vocabulary matching, and the normalised values are correctly mapped to the corresponding `Concept` objects.
3. **Given** a spreadsheet row with an invalid controlled-vocabulary value, **When** the importer processes it, **Then** a descriptive validation error is raised identifying the row number, column name, and invalid value.
4. **Given** an import is run twice with the same file, **When** the importer detects existing records, **Then** records are updated rather than duplicated using template-aware keys: if `ID` / `ID_parent` are present they map to `HeatFlow.local_id` and parent `local_id`; if those columns are absent (standard individual-dataset upload template), parent upsert uses `lat_NS` + `long_EW` and child upsert uses `lat_NS` + `long_EW` + `q_top` + `q_bottom` + `publication_reference`, without raising header-validation errors for missing `ID` / `ID_parent` columns.
5. **Given** an authenticated staff user opens the GHFDB admin import page, **When** the import form is rendered, **Then** the page loads without server error and exposes the configured import resource classes for selection.
6. **Given** a standard upload template (no `ID_parent` column) is imported, **When** the confirm-page diff view is rendered before the user clicks "Confirm Import", **Then** the `ID_parent` column shows either the actual `ParentHeatFlow.local_id` value or is empty — the internal `AUTO_PARENT:<lat>:<lon>` synthetic key MUST NOT appear in any user-facing confirm-page output.
7. **Given** any GHFDB XLSX file is imported, **When** the confirm-page diff view is rendered, **Then** the columns are presented in the same left-to-right order as the uploaded spreadsheet template — `PARENT_COLUMNS` order for the parent resource and `GHFDB_COLUMN_ORDER` order for the child resource — so that staff can verify imported values by matching them against the source file column-by-column.
8. **Given** a spreadsheet cell whose value the XLSX loader has interpreted as a number is passed to a widget that expects a **text string** (e.g. a vocabulary label or site name), **When** the importer processes it, **Then** a descriptive `ValueError` is raised that names the column and the unexpected value — **not** a bare `AttributeError: 'int' object has no attribute 'strip'` — so the user can locate and correct the offending cell. This guard applies to `ConceptWidget` (vocabulary columns) and `ParentWidget` (`name` column). (BUG-007)
9. **Given** a spreadsheet cell in a **numeric quantity column** (e.g. `T_grad_mean`, `tc_mean`) holds a native Python `int` or `float` (the normal output of openpyxl for numeric cells), **When** the importer processes it, **Then** the sentinel check treats the value as **present** and proceeds to create the related sub-record (`ThermalGradient`, `IntervalConductivity`) with the correct Pint quantity value — the row is **not** rejected with a `ValueError`. (BUG-008)
10. **Given** a spreadsheet row contains a non-empty `geo_stratigraphy` value (e.g. `"Holocene"`), **When** the importer processes it, **Then** the value is normalised, matched to a `GeologicalTimescale` `Concept`, and stored on `HeatFlowInterval.age` (a `ConceptManyToManyField` backed by `research_vocabs.Concept`) — the import MUST NOT raise `"Field 'id' expected a number but got <gts2020: Holocene>"` or any cross-model type error. `HeatFlowInterval.stratigraphy` (M2M to `stratigraphy.StratigraphicUnit`) is a distinct field and MUST remain unset by this mapping. (BUG-009)

---

### User Story 3 - Export Heat Flow Data to GHFDB Spreadsheet Format (Priority: P2)

A data manager wants to produce an official GHFDB-compliant spreadsheet (XLSX) from all or a filtered subset of the application's heat-flow data, for submission to the IHFC repository or for sharing with collaborators. The export is triggered from the Django admin site, accessible to staff only.

**Why this priority**: Equal priority to import — the round-trip is only complete when export is working. The existing download view serves a static file; this story replaces it with a dynamically generated GHFDB-structured output.

**Independent Test**: Can be tested by exporting a known dataset from the admin and comparing the resulting spreadsheet columns, headers, and values against the reference GHFDB template.

**Acceptance Scenarios**:

1. **Given** the application contains heat-flow records, **When** a staff user triggers the export action from the Django admin, **Then** a valid XLSX file is produced whose columns match the official GHFDB spreadsheet schema in the correct order.
2. **Given** a queryset filtered by dataset or other criteria, **When** the export is triggered for that subset, **Then** only matching records appear in the output file.
3. **Given** multi-value fields stored as many-to-many relations (e.g., `explo_purpose`, `tc_method`), **When** exported, **Then** they are serialised as semicolon-separated strings matching the GHFDB convention.
4. **Given** Pint quantity fields (e.g., heat flow in mW/m²), **When** exported, **Then** values are written as plain numeric values in the correct SI units without unit symbols.

---

### Edge Cases

- What happens when a GHFDB spreadsheet contains rows with missing mandatory fields (e.g., latitude, longitude, heat flow value)? The importer collects these as validation errors and rolls back the entire import, reporting all such rows together.
- What happens when the same site name, latitude, and longitude match multiple existing records? The importer applies a fixed upsert strategy: if a record with the same `local_id` already exists it is updated; otherwise a new record is created. Skip and error-on-duplicate strategies are out of scope for this feature and deferred to a future spec.
- What happens when the uploaded spreadsheet follows the standard individual-dataset template and omits `ID` / `ID_parent`? The importer must switch to natural keys: `lat_NS` + `long_EW` for parent rows and `lat_NS` + `long_EW` + `q_top` + `q_bottom` + `publication_reference` for child rows, and this path must not fail due to `import_id_fields` header checks on missing optional ID columns.
- What happens when controlled-vocabulary cells include bracket-wrapped values and casing differences from vocabulary definitions (for example, `[Onshore (continental)]`)? The importer must normalise tokens by removing square brackets and lowercasing prior to vocabulary validation and lookup.
- What happens when exporting a very large dataset (tens of thousands of rows)? The export must use `.iterator()` or stream the response rather than loading everything into memory, or clearly document the row limit before which a background-task approach is required.
