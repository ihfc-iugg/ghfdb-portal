# Feature Specification: GHFDB Product Layer

**Feature Branch**: `002-ghfdb-product-utilities`
**Created**: 2026-04-10
**Status**: Draft
**References**: Fuchs et al. (2021); Fuchs et al. (2023); IHFC GHFDB v2024
**Input**: User description: "GHFDB product layer: proxy model, round-trip spreadsheet utilities, and web map viewer"

## Overview

This feature treats the Global Heat Flow Database (GHFDB) as a first-class product within the application, distinct from the underlying `heat_flow` scientific data model. The `project/ghfdb` app becomes the home for all GHFDB-product-layer concerns: a flat proxy model that mirrors the GHFDB spreadsheet structure, round-trip import/export utilities (both staff-only via the Django admin) that convert between the flat spreadsheet format and the normalised heat_flow relational model, and a dedicated "Explore" page that embeds the GHFDB web-map viewer inside a full-screen iframe with a main-menu link for easy access.

**Out of scope (deferred):** Scheduled or automated release generation; public/anonymous downloadable exports. Portal users browse data live via the portal UI. Automated release pipelines will be specified in a separate feature.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - GHFDB Proxy Model for Efficient Flat Queries (Priority: P1)

A developer or data curator needs to query heat flow records in the exact flat structure used by the GHFDB spreadsheet product — one row per child heat-flow measurement along with all parent-site, thermal-gradient, and thermal-conductivity columns — without writing complex multi-join queries every time.

**Why this priority**: The proxy model is the foundation that every other GHFDB product feature (export, admin display, API, map) depends on. Without a well-optimised flat view of the data, downstream features require duplicated query logic.

**Independent Test**: Can be tested independently by querying the proxy model and verifying that a single queryset call returns all expected GHFDB columns without N+1 queries.

**Acceptance Scenarios**:

1. **Given** the database contains a `HeatFlow` record with linked site, parent, thermal-gradient, and thermal-conductivity data, **When** the GHFDB proxy queryset's `as_ghfdb_flat()` method is called, **Then** each record is returned as a flat structure containing all required GHFDB spreadsheet columns with no additional queries per row.
2. **Given** the proxy model is used in the Django ORM, **When** standard queryset operations (filter, order_by, count) are applied, **Then** they behave identically to the underlying `HeatFlow` model.
3. **Given** the proxy model, **When** accessed from the Django admin, **Then** it appears as a separate, read-oriented admin view labelled "GHFDB Entries".

---

### User Story 2 - Import GHFDB Spreadsheet into Heat Flow Data Model (Priority: P2)

A data manager has a GHFDB-format XLSX or CSV file exported from the official IHFC spreadsheet template. They want to ingest it into the application's normalised heat_flow data model without manually mapping every column.

**Why this priority**: Ingesting official GHFDB releases is the primary data-loading workflow. The existing `resources.py` contains partial import logic; this story formalises and completes it as a first-class utility.

**Independent Test**: Can be tested by providing a sample GHFDB spreadsheet and confirming that the resulting database records match the spreadsheet rows exactly, including controlled-vocabulary mappings and multi-value semicolon-separated fields.

**Acceptance Scenarios**:

1. **Given** a valid GHFDB XLSX file, **When** the import utility is run, **Then** `HeatFlow`, `HeatFlowSite`, `ParentHeatFlow`, `ThermalGradient`, and `IntervalConductivity` records are created with correct field mappings.
2. **Given** a spreadsheet row containing semicolon-separated controlled-vocabulary values (e.g., `q_method`, `tc_method`), **When** the importer processes it, **Then** the values are correctly mapped to the corresponding `Concept` objects.
3. **Given** a spreadsheet row with an invalid controlled-vocabulary value, **When** the importer processes it, **Then** a descriptive validation error is raised identifying the row number, column name, and invalid value.
4. **Given** an import is run twice with the same file, **When** the importer detects existing records using the `ID` value (matched against `HeatFlow.local_id`) and `ID_parent` value (matched against the parent model's `local_id`), **Then** records are updated rather than duplicated.

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

### User Story 4 - Web Map Viewer Page with Main Menu Link (Priority: P3)

A portal visitor wants a quick visual overview of the global heat flow distribution. They click a "Map" (or "Explore") link in the application's top navigation bar and see the GHFDB interactive web-map viewer embedded inside the portal page.

**Why this priority**: Lower priority than the data utilities since it is a UI convenience feature, but it is a direct user-facing deliverable that increases portal discoverability.

**Independent Test**: Can be tested independently by navigating to the map URL and confirming the iframe loads and the menu link is active, with no dependency on import/export functionality.

**Acceptance Scenarios**:

1. **Given** a logged-in or anonymous user, **When** they click the "Explore" menu item in the main navigation, **Then** they are taken to a portal page that renders the GHFDB web-map viewer inside a responsive, full-viewport iframe.
2. **Given** the map page, **When** it loads, **Then** no horizontal scrollbars appear and the iframe fills the available viewport height.
3. **Given** the main application menu, **When** the user is on the map page, **Then** the "Explore" menu item is marked as active/current.

---

### Edge Cases

- What happens when a GHFDB spreadsheet contains rows with missing mandatory fields (e.g., latitude, longitude, heat flow value)? The importer collects these as validation errors and rolls back the entire import, reporting all such rows together.
- What happens when the same site name, latitude, and longitude match multiple existing records? The importer applies a fixed upsert strategy: if a record with the same `local_id` already exists it is updated; otherwise a new record is created. Skip and error-on-duplicate strategies are out of scope for this feature and deferred to a future spec.
- What happens when exporting a very large dataset (tens of thousands of rows)? The export must stream the response rather than loading everything into memory, or clearly document the row limit before which a background-task approach is required.
- What happens when the map viewer iframe URL is unreachable? The page must degrade gracefully, showing an informative message rather than a blank frame.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a Django proxy model (`GHFDB`) backed by `HeatFlow` with a custom queryset that returns all GHFDB spreadsheet columns via an optimised single-query path (select_related and prefetch_related).
- **FR-002**: The proxy model's queryset MUST expose a named method (e.g., `as_ghfdb_flat()`) that annotates or selects all columns required by the GHFDB output schema.
- **FR-003**: The system MUST provide an import utility (building on existing `resources.py` logic) that accepts a GHFDB-format XLSX file (`.xlsx` only; CSV is not supported — see research decision R10) and populates `HeatFlow`, `HeatFlowSite`, `ParentHeatFlow`, `ThermalGradient`, and `IntervalConductivity` records. The import is triggered exclusively via the Django admin site using django-import-export's built-in admin action and is restricted to staff users.
- **FR-004**: The importer MUST correctly translate semicolon-separated controlled-vocabulary display labels in spreadsheet columns (such as `q_method`, `tc_method`, `explo_purpose`) to the corresponding `Concept` ORM objects stored in the database.
- **FR-005**: The importer MUST validate all rows before persisting any data. If any row fails validation (including invalid controlled-vocabulary values, missing mandatory fields, or type errors), the entire import MUST be rolled back and the complete list of row-level errors (row number, column name, invalid value) returned to the user with no records written to the database.
- **FR-006**: The importer MUST support an upsert strategy using the spreadsheet's `ID` column (mapped to `HeatFlow.local_id`) and `ID_parent` column (mapped to `ParentHeatFlow.local_id` / `HeatFlowSite.local_id`) as the stable identifiers: if a matching record exists it is updated; otherwise a new record is created.
- **FR-007**: The system MUST provide an export utility that produces a valid GHFDB-format XLSX file from any `HeatFlow` queryset (or the full database). The export is triggered exclusively via the Django admin site using django-import-export's built-in admin action and is restricted to staff users.
- **FR-008**: The export MUST write all GHFDB spreadsheet columns in the prescribed column order, using semicolons to join multi-value fields and writing Pint quantity values as plain unit-stripped numerics in SI units.
- **FR-009**: The system MUST provide a URL-accessible view at `ghfdb/explore/` (or equivalent) that renders an HTML template embedding the GHFDB web-map viewer (`https://ihfc-iugg.github.io/HeatFlowMapping/`) inside a full-screen iframe. The URL is hardcoded in the template.
- **FR-010**: A menu item labelled "Explore" (or equivalent) MUST be registered in the main application navigation bar pointing to the map viewer URL.
- **FR-011**: The proxy model MUST be registerable with the Django admin (read-only mode is acceptable) so staff can inspect GHFDB-structured entries without modifying underlying normalised records.

### Key Entities

- **GHFDB (proxy)**: A read-oriented proxy over `HeatFlow` that presents heat-flow records in the flat GHFDB spreadsheet schema. Does not add database columns; adds custom manager (`GHFDBManager`) and queryset (`GHFDBQuerySet`) methods for efficient flat-data retrieval. `verbose_name = "GHFDB Entry"`, `verbose_name_plural = "GHFDB Entries"`.
- **GHFDBImportResource**: The import resource class (extending the existing `resources.py` work) that maps GHFDB spreadsheet columns to the normalised heat_flow model graph.
- **GHFDBExportResource**: An export resource that serialises the normalised heat_flow model graph back into the flat GHFDB spreadsheet structure, handling unit stripping and vocabulary label rendering.
- **GHFDBExploreView**: A `TemplateView` subclass that renders the map viewer page. The iframe URL (`https://ihfc-iugg.github.io/HeatFlowMapping/`) is hardcoded directly in the template; no Django setting is required.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A GHFDB spreadsheet roundtrip (import then export) results in an output file whose values differ from the input by less than floating-point rounding for numeric fields and zero difference for text/vocabulary fields.
- **SC-002**: Querying all records via `GHFDB.objects.as_ghfdb_flat()` executes in a constant number of database queries regardless of the number of records returned (no N+1 queries).
- **SC-003**: A data manager can import a 10,000-row GHFDB spreadsheet and receive a complete validation error report (all invalid rows, not just the first) within 60 seconds.
- **SC-004**: The map viewer page loads and displays the iframe within 3 seconds on a standard broadband connection.
- **SC-005**: 100% of GHFDB spreadsheet columns defined in the Fuchs et al. (2023) schema are covered by both the import and export utilities with no undocumented omissions.

## Clarifications

### Session 2026-04-10

- Q: Where does a user trigger GHFDB spreadsheet import? → A: Django admin — import triggered from the admin site using django-import-export's built-in admin action (staff only).
- Q: What is the stable identifier used to detect and upsert existing records during import? → A: The spreadsheet's `ID` column maps to `local_id` on the child `HeatFlow` model; `ID_parent` maps to `local_id` on the parent model (`ParentHeatFlow`/`HeatFlowSite`). Both fields are used together to identify and upsert entries.
- Q: What is the rollback behaviour when a batch import contains some invalid rows? → A: Atomic — the entire file is validated first; if any row fails validation, nothing is saved and the complete error list is returned to the user.
- Q: Where/how does export work — public download, admin action, or deferred? → A: Admin-only via django-import-export's admin export action (staff only), symmetric with import. Automated/scheduled release pipelines are deferred to a future spec.
- Q: What is the default iframe URL for the map viewer, and should it be a configurable Django setting? → A: Hardcoded to `https://ihfc-iugg.github.io/HeatFlowMapping/` directly in the template. No Django setting required.

## Assumptions

- The official GHFDB spreadsheet column schema is defined by the Fuchs et al. (2023) publication and the `ghfdb_colmeta.json` metadata file already present in the codebase; no new column definitions will be introduced as part of this feature.
- The web-map viewer iframe URL (`https://ihfc-iugg.github.io/HeatFlowMapping/`) is hardcoded directly in the template; no Django setting is required.
- Large file imports may be moved to background tasks in a future feature; synchronous (in-request) processing is acceptable for this feature for files up to a reasonable size limit (e.g., 50,000 rows / 20 MB).
- The import utility will reuse and refactor the existing `resources.py` code rather than rewriting it from scratch.
- Import and export are both accessible only via the Django admin site (django-import-export integration); no standalone portal UI or management commands are in scope for this feature.
- Automated or scheduled release generation (e.g., publishing a versioned GHFDB XLSX on a cron schedule) is explicitly deferred to a future spec.
- The proxy model does not introduce additional database tables or migrations.
- The menu entry for the map viewer is added to the existing `heat_flow/menus.py` (or a new `ghfdb/menus.py`) using the `flex_menu` pattern already established in the project.
