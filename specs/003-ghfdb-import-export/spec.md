# Feature Specification: GHFDB Import/Export Pipeline

**Feature Branch**: `003-ghfdb-import-export`
**Created**: 2026-04-15 (split from `002-ghfdb-proxy`)
**Status**: Complete
**Dependency**: Requires `002-ghfdb-proxy` — GHFDB proxy model, `GHFDBChildManager.for_export()`, and `local_id` fields on `HeatFlow`, `HeatFlowSite`, and `ParentHeatFlow`.
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
**Refined**: 2026-04-20 — Added second XLSX importer format (5 metadata rows, header row 6, data from row 7) and admin format-selection requirement; added Acceptance Scenarios 11 and 12.
**Refined**: 2026-04-23 — `project/ghfdb/constants.py` was updated to add `PARENT_COLUMNS`, `CHILD_COLUMNS`, and `META_FIELDS` as canonical ordered lists representing the GHFDB spreadsheet columns in template order (case-sensitive, matching row 6 of the official IHFC XLSX). `GHFDB_COLUMN_ORDER` is now derived as `PARENT_COLUMNS + CHILD_COLUMNS + META_FIELDS`. These four lists are the single source of truth for the GHFDB flat spreadsheet column structure; all import/export resources and queryset annotations MUST align to them. The stale hardcoded lowercase 62-column tuple (`GHFDB_COLUMN_ORDER: tuple[str, ...]`) that previously existed alongside these lists MUST be removed. See BUG-010 for the remaining implementation requirements.
**Bugfix**: 2026-04-23 — [BUG-010] Four implementation changes MUST be made to align code with the updated canonical constants. (1) Remove the old hardcoded lowercase `GHFDB_COLUMN_ORDER` tuple from `constants.py` — the derived list takes precedence but the tuple creates confusion and must be deleted. (2) Rename all scalar annotation keys in `GHFDBChildQuerySet.as_ghfdb_flat()` to match the canonical names from `PARENT_COLUMNS` and `CHILD_COLUMNS` exactly (including case), e.g. `"name"`, `"lat_NS"`, `"long_EW"`, `"elevation"`, `"environment"`, `"p_comment"`, `"corr_HP_flag"`, `"total_depth_MD"`, `"total_depth_TVD"`, `"explo_method"`, `"ID_parent"`, `"q"`, `"q_uncertainty"` instead of the old prefixed/lowercase variants. (3) Add `as_ghfdb_flat()` to `GHFDBParentQuerySet` (and its matching manager delegate) that annotates all scalar `PARENT_COLUMNS` fields against the `ParentHeatFlow` / `HeatFlowSite` model paths, with annotation keys matching `PARENT_COLUMNS` names exactly. (4) Update `GHFDBChildImportResource.get_user_visible_fields()` column-order lookup so that both the lookup-dict keys AND the field `column_name` values are lowercased before matching — since `GHFDB_COLUMN_ORDER` now contains mixed-case names (e.g. `T_grad_mean`, `lat_NS`, `corr_HP_flag`), the previous one-sided `.lower()` on `column_name` is insufficient. Updated Acceptance Scenario 13.
**References**: Fuchs et al. (2021); Fuchs et al. (2023); IHFC GHFDB v2024
**Split from**: `002-ghfdb-proxy` — User Stories 2 & 3

## Overview

This feature implements the GHFDB round-trip import/export pipeline within the `project/ghfdb` app. A `resources/` package provides:

1. **Parent import resource** (`GHFDBParentImportResource`) — ingests parent-level site records from an official GHFDB XLSX spreadsheet into `HeatFlowSite`, `ParentHeatFlow`, and supporting models.
2. **Child import resource** (`GHFDBChildImportResource`) — ingests child heat-flow measurements and all sub-records (`HeatFlow`, `HeatFlowInterval`, `ThermalGradient`, `IntervalConductivity`, `HeatFlowCorrection`, `ProbeMetadata`).
3. **Export resource** (`GHFDBExportResource`) — serialises the normalised database back to the flat GHFDB spreadsheet format using the `GHFDB` proxy model's `for_export()` queryset (from `002-ghfdb-proxy`).

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
11. **Given** a valid XLSX file whose layout is the **simple template format** (rows 1–5 are arbitrary metadata, row 6 contains column headers, and data rows begin at row 7 with no intervening unit-label or allowed-range rows), **When** the admin user selects the "GHFDB Simple Template" import format and uploads the file, **Then** the importer reads column headers from row 6, begins iterating data from row 7, and creates/updates the same set of records (with the same field-mapping widgets and upsert logic) as the standard official-template import — no data rows are lost to metadata-row skipping and no server error occurs.
12. **Given** an authenticated staff user opens the GHFDB admin import page, **When** the import format selection control is presented, **Then** two named format options are available — "GHFDB Official Template" (header row 6, skip unit-label row 7 and allowed-range row 8, data from row 9) and "GHFDB Simple Template" (header row 6, data from row 7) — and selecting either option causes the importer to apply the correct row-skip logic for that format without any additional configuration by the user.
13. **Given** `GHFDB_COLUMN_ORDER` now contains mixed-case column names (e.g. `T_grad_mean`, `lat_NS`, `corr_HP_flag`), **When** `GHFDBChildImportResource.get_user_visible_fields()` builds its column-order lookup, **Then** it MUST lowercase both the lookup-dict keys (from `GHFDB_COLUMN_ORDER`) and the field `column_name` values before matching — a one-sided `.lower()` applied only to `column_name` will fail to find mixed-case entries and incorrectly sort those fields to the end of the confirm-page diff. (BUG-010)

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
5. **Given** the canonical annotation keys in `GHFDBChildQuerySet.as_ghfdb_flat()` MUST match `PARENT_COLUMNS` / `CHILD_COLUMNS` names exactly (including case), **When** `GHFDBExportResource` field declarations reference these annotations via `attribute=`, **Then** every `attribute=` value MUST be updated to match the renamed annotation key — stale lowercase attribute names (e.g. `attribute="site_name"`, `attribute="p_q"`, `attribute="total_depth_md"`) will silently export empty columns. (BUG-010)
6. **Given** `GHFDBParentQuerySet` needs a flat-row annotation method symmetric to the child queryset, **When** `GHFDBParentQuerySet.as_ghfdb_flat()` is called, **Then** it MUST annotate all scalar `PARENT_COLUMNS` fields using the canonical column names as annotation keys (e.g. `"q"`, `"name"`, `"lat_NS"`, `"elevation"`, `"corr_HP_flag"`) and return the annotated queryset; the `GHFDBParentManager` MUST expose a matching delegate method. (BUG-010)

---

### Edge Cases

- What happens when a GHFDB spreadsheet contains rows with missing mandatory fields (e.g., latitude, longitude, heat flow value)? The importer collects these as validation errors and rolls back the entire import, reporting all such rows together.
- What happens when the same site name, latitude, and longitude match multiple existing records? The importer applies a fixed upsert strategy: if a record with the same `local_id` already exists it is updated; otherwise a new record is created. Skip and error-on-duplicate strategies are out of scope for this feature and deferred to a future spec.
- What happens when the uploaded spreadsheet follows the standard individual-dataset template and omits `ID` / `ID_parent`? The importer must switch to natural keys: `lat_NS` + `long_EW` for parent rows and `lat_NS` + `long_EW` + `q_top` + `q_bottom` + `publication_reference` for child rows, and this path must not fail due to `import_id_fields` header checks on missing optional ID columns.
- What happens when controlled-vocabulary cells include bracket-wrapped values and casing differences from vocabulary definitions (for example, `[Onshore (continental)]`)? The importer must normalise tokens by removing square brackets and lowercasing prior to vocabulary validation and lookup.
- What happens when exporting a very large dataset (tens of thousands of rows)? The export must use `.iterator()` or stream the response rather than loading everything into memory, or clearly document the row limit before which a background-task approach is required.
- What happens when a user accidentally selects the wrong import format (e.g., uploads an official-template file but selects the simple template)? The importer will process row 7 as the first data row; for official-template files row 7 is the unit-label row and its cells will likely fail vocabulary or type validation, producing descriptive per-field errors that the user can use to identify the format mismatch. The importer MUST NOT silently corrupt data — validation errors surfaced by the wrong format choice are the expected safeguard.
