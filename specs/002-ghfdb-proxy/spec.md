# Feature Specification: GHFDB Flat Data Interface

**Feature Branch**: `002-ghfdb-proxy`
**Created**: 2026-04-10
**Status**: Complete
**Refined**: 2026-04-14 — Added explicit GHFDB Entry admin column order plus required search and filter fields for parent-level spreadsheet attributes.
**Bugfix**: 2026-04-14 — [BUG-001] Added constrained-option behavior for `explo_purpose` admin filtering so list-filter choices are vocabulary-scoped.
**References**: Fuchs et al. (2021); Fuchs et al. (2023); IHFC GHFDB v2024
**Input**: User description: "GHFDB product layer: proxy model, flat query interface, and web map viewer"
**Downstream**: Import/export pipeline is specified separately in `003-ghfdb-import-export`.

## Overview

This feature establishes the GHFDB flat data interface within the `project/ghfdb` app: a `GHFDB` proxy model over `HeatFlow` with an optimised `GHFDBQuerySet` that returns all GHFDB columns as a flat annotated structure without N+1 queries, a read-oriented Django admin changelist labelled "GHFDB Entries", and a dedicated "Explore" page that embeds the GHFDB web-map viewer inside a full-screen iframe with a main-menu link for easy access.

**Downstream feature**: Round-trip import/export utilities (staff-only admin, XLSX, vocabulary normalisation) are specified in `003-ghfdb-import-export`. That spec depends on the `GHFDB` proxy model and `GHFDBManager.for_export()` queryset produced by this spec.

**Out of scope (deferred):** Scheduled or automated release generation; public/anonymous downloadable exports.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - GHFDB Proxy Model for Efficient Flat Queries (Priority: P1)

A developer or data curator needs to query heat flow records in the exact flat structure used by the GHFDB spreadsheet product — one row per child heat-flow measurement along with all parent-site, thermal-gradient, and thermal-conductivity columns — without writing complex multi-join queries every time.

**Why this priority**: The proxy model is the foundation that every other GHFDB product feature (export, admin display, API, map) depends on. Without a well-optimised flat view of the data, downstream features require duplicated query logic.

**Independent Test**: Can be tested independently by querying the proxy model and verifying that a single queryset call returns all expected GHFDB columns without N+1 queries.

**Acceptance Scenarios**:

1. **Given** the database contains a `HeatFlow` record with linked site, parent, thermal-gradient, and thermal-conductivity data, **When** the GHFDB proxy queryset's `as_ghfdb_flat()` method is called, **Then** each record is returned as a flat structure containing all required GHFDB spreadsheet columns with no additional queries per row.
2. **Given** the proxy model is used in the Django ORM, **When** standard queryset operations (filter, order_by, count) are applied, **Then** they behave identically to the underlying `HeatFlow` model.
3. **Given** the proxy model, **When** accessed from the Django admin, **Then** it appears as a separate, read-oriented admin view labelled "GHFDB Entries".
4. **Given** the GHFDB Entry admin changelist, **When** a staff user views records, **Then** the displayed parent-level columns are in this exact order: `ID_parent`, `q`, `q_uncertainty`, `name`, `lat_NS`, `long_EW`, `elevation`, `environment`, `corr_HP_flag`, `total_depth_MD`, `total_depth_TVD`, `explo_method`, `explo_purpose`, `country`, `region`, `continent`, `domain`.
5. **Given** the GHFDB Entry admin changelist, **When** a staff user uses search and filters, **Then** search is supported by `name` and `ID_parent`, list filters are available for `environment`, `corr_HP_flag`, `explo_method`, `explo_purpose`, `country`, `region`, `continent`, and `domain`, and `explo_purpose` filter choices are restricted to values accepted by the `HeatFlowSite.explo_purpose` vocabulary.

---

### Edge Cases

- What happens when a `HeatFlowCorrection` for a specific type doesn't exist for a given `HeatFlow` record? The correction subquery annotation returns `None` for that field.
- What happens when `thermal_gradient` or `thermal_conductivity` is `null` on a `HeatFlow` record? All related annotations return `None`; the queryset still returns the row without error.
- What happens when the map viewer iframe URL is unreachable? The page must degrade gracefully, showing an informative message rather than a blank frame.

A portal visitor wants a quick visual overview of the global heat flow distribution. They click a "Map" (or "Explore") link in the application's top navigation bar and see the GHFDB interactive web-map viewer embedded inside the portal page.

**Why this priority**: Lower priority than the data utilities since it is a UI convenience feature, but it is a direct user-facing deliverable that increases portal discoverability.

**Independent Test**: Can be tested independently by navigating to the map URL and confirming the iframe loads and the menu link is active, with no dependency on import/export functionality.

**Acceptance Scenarios**:

1. **Given** a logged-in or anonymous user, **When** they click the "Explore" menu item in the main navigation, **Then** they are taken to a portal page that renders the GHFDB web-map viewer inside a responsive, full-viewport iframe.
2. **Given** the map page, **When** it loads, **Then** no horizontal scrollbars appear and the iframe fills the available viewport height.
3. **Given** the main application menu, **When** the user is on the map page, **Then** the "Explore" menu item is marked as active/current.

---

### Edge Cases

- What happens when a `HeatFlowCorrection` for a specific type doesn't exist for a given `HeatFlow` record? The correction subquery annotation returns `None` for that field.
- What happens when `thermal_gradient` or `thermal_conductivity` is `null` on a `HeatFlow` record? All related annotations return `None`; the queryset still returns the row without error.
- What happens when the map viewer iframe URL is unreachable? The page must degrade gracefully, showing an informative message rather than a blank frame.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a Django proxy model (`GHFDB`) backed by `HeatFlow` with a custom queryset that returns all GHFDB spreadsheet columns via an optimised single-query path (select_related and prefetch_related).
- **FR-002**: The proxy model's queryset MUST expose a named method (e.g., `as_ghfdb_flat()`) that annotates or selects all columns required by the GHFDB output schema.
- **FR-003**: The system MUST provide an import utility (building on existing `resources.py` logic) that accepts a GHFDB-format XLSX file (`.xlsx` only; CSV is not supported — see research decision R10) and populates `HeatFlow`, `HeatFlowSite`, `ParentHeatFlow`, `ThermalGradient`, and `IntervalConductivity` records. The import is triggered exclusively via the Django admin site using django-import-export's built-in admin action and is restricted to staff users. The admin import view MUST render successfully for authenticated staff users, including resource-class selection hooks that remain compatible with the installed django-import-export version.
- **FR-004**: The importer MUST correctly translate semicolon-separated controlled-vocabulary display labels in spreadsheet columns (such as `q_method`, `tc_method`, `explo_purpose`) to the corresponding `Concept` ORM objects stored in the database.
- **FR-005**: The importer MUST validate all rows before persisting any data. If any row fails validation (including invalid controlled-vocabulary values, missing mandatory fields, or type errors), the entire import MUST be rolled back and the complete list of row-level errors (row number, column name, invalid value) returned to the user with no records written to the database.
- **FR-006**: The importer MUST support a template-aware upsert strategy. When `ID` and `ID_parent` columns are present, they map to `HeatFlow.local_id` and `ParentHeatFlow.local_id` / `HeatFlowSite.local_id` respectively. When those columns are absent (standard individual-dataset upload template), parent upsert MUST use `lat_NS` + `long_EW`, and child upsert MUST use `lat_NS` + `long_EW` + `q_top` + `q_bottom` + `publication_reference`. The implementation MUST be header-validation-safe: `import_id_fields` MUST reference columns guaranteed to exist in the uploaded template path, and missing optional `ID` / `ID_parent` headers MUST NOT cause import rejection. In all cases, if a matching record exists it is updated; otherwise a new record is created.
- **FR-007**: The system MUST provide an export utility that produces a valid GHFDB-format XLSX file from any `HeatFlow` queryset (or the full database). The export is triggered exclusively via the Django admin site using django-import-export's built-in admin action and is restricted to staff users.
- **FR-008**: The export MUST write all GHFDB spreadsheet columns in the prescribed column order, using semicolons to join multi-value fields and writing Pint quantity values as plain unit-stripped numerics in SI units.
- **FR-009**: The system MUST provide a URL-accessible view at `ghfdb/explore/` (or equivalent) that renders an HTML template embedding the GHFDB web-map viewer (`https://ihfc-iugg.github.io/HeatFlowMapping/`) inside a full-screen iframe. The URL is hardcoded in the template.
- **FR-010**: A menu item labelled "Explore" (or equivalent) MUST be registered in the main application navigation bar pointing to the map viewer URL.
- **FR-011**: The proxy model MUST be registerable with the Django admin (read-only mode is acceptable) so staff can inspect GHFDB-structured entries without modifying underlying normalised records.
- **FR-012**: The GHFDB Entry Django admin changelist MUST display these parent-level GHFDB spreadsheet fields in this exact order: `ID_parent`, `q`, `q_uncertainty`, `name`, `lat_NS`, `long_EW`, `elevation`, `environment`, `corr_HP_flag`, `total_depth_MD`, `total_depth_TVD`, `explo_method`, `explo_purpose`, `country`, `region`, `continent`, `domain`.
- **FR-013**: The GHFDB Entry Django admin changelist MUST support text search on `name` and `ID_parent`.
- **FR-014**: The GHFDB Entry Django admin changelist MUST provide filters for `environment`, `corr_HP_flag`, `explo_method`, `explo_purpose`, `country`, `region`, `continent`, and `domain`.
- **FR-015**: For concept-backed admin list filters, filter options MUST be constrained to vocabulary-accepted values for the target field. Specifically, the `explo_purpose` filter MUST only show values accepted by `HeatFlowSite.explo_purpose` and MUST NOT show unrelated `Concept` values.
- **FR-016**: Before validating or mapping controlled-vocabulary spreadsheet values, the importer MUST normalise each token by removing surrounding square brackets (for example, `[Onshore (continental)]` -> `Onshore (continental)`) and converting the result to lowercase so standard GHFDB upload-template values remain compatible with lowercase vocabulary definitions.

### Key Entities

- **GHFDB (proxy)**: A read-oriented proxy over `HeatFlow` that presents heat-flow records in the flat GHFDB spreadsheet schema. Does not add database columns; adds custom manager (`GHFDBManager`) and queryset (`GHFDBQuerySet`) methods for efficient flat-data retrieval. `verbose_name = "GHFDB Entry"`, `verbose_name_plural = "GHFDB Entries"`.
- **GHFDBParentImportResource**: The parent import resource that maps the 18 parent-level GHFDB spreadsheet columns to `HeatFlowSite` and `ParentHeatFlow` records, using `ParentWidget` for related-model creation and template-aware upsert (`ID_parent`/`local_id` when available, otherwise `lat_NS` + `long_EW`) while remaining safe when `ID_parent` is absent from file headers.
- **GHFDBChildImportResource**: The child import resource that maps the remaining GHFDB spreadsheet columns to `HeatFlow`, `ThermalGradient`, `IntervalConductivity`, `HeatFlowCorrection`, and `ProbeMetadata` records, using `IntervalWidget`, `GradientWidget`, and `ConductivityWidget` for sub-model handling and template-aware upsert (`ID`/`local_id` when available, otherwise `lat_NS` + `long_EW` + `q_top` + `q_bottom` + `publication_reference`) while remaining safe when `ID`/`ID_parent` are absent from file headers.
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
- Q: What is the stable identifier used to detect and upsert existing records during import? → A: The importer uses a template-aware identifier strategy: with official-release sheets, `ID`/`ID_parent` map to child/parent `local_id`; with standard individual-dataset uploads that omit these fields, parent rows use `lat_NS` + `long_EW` and child rows use `lat_NS` + `long_EW` + `q_top` + `q_bottom` + `publication_reference`.
- Q: What is the rollback behaviour when a batch import contains some invalid rows? → A: Atomic — the entire file is validated first; if any row fails validation, nothing is saved and the complete error list is returned to the user.
- Q: Where/how does export work — public download, admin action, or deferred? → A: Admin-only via django-import-export's admin export action (staff only), symmetric with import. Automated/scheduled release pipelines are deferred to a future spec.
- Q: What is the default iframe URL for the map viewer, and should it be a configurable Django setting? → A: Hardcoded to `https://ihfc-iugg.github.io/HeatFlowMapping/` directly in the template. No Django setting required.

### Session 2026-04-15

- Q: What should happen if uploaded template headers omit `ID_parent` and `ID` entirely? → A: Import must still proceed through natural-key upsert paths without failing `import_id_fields` header validation; optional ID headers cannot be required for standard-upload imports.
- Q: How should controlled-vocabulary values from standard templates be handled when values are wrapped in square brackets and/or use mixed case? → A: Normalise each token by removing `[` and `]` and converting to lowercase before vocabulary validation and Concept mapping.
- Q: What is the exact row structure of the GHFDB upload template? → A: The template has 8 preamble rows before any data. Row 1 = ID, row 2 = Obligation, row 3 = Domain, row 4 = Quality Relevance, row 5 = Name, row 6 = Short Name (**column headers — used**), row 7 = Unit (skipped), row 8 = Allowed range of values (skipped). Data rows begin at row 9. `GHFDBImportFormat` MUST read headers from row 6 and start data iteration at `min_row=9`.

## Assumptions

- The official GHFDB spreadsheet column schema is defined by the Fuchs et al. (2023) publication and the `ghfdb_colmeta.json` metadata file already present in the codebase; no new column definitions will be introduced as part of this feature.
- The web-map viewer iframe URL (`https://ihfc-iugg.github.io/HeatFlowMapping/`) is hardcoded directly in the template; no Django setting is required.
- Large file imports may be moved to background tasks in a future feature; synchronous (in-request) processing is acceptable for this feature for files up to a reasonable size limit (e.g., 50,000 rows / 20 MB).
- Import and export are both accessible only via the Django admin site (django-import-export integration); no standalone portal UI or management commands are in scope for this feature.
- Automated or scheduled release generation (e.g., publishing a versioned GHFDB XLSX on a cron schedule) is explicitly deferred to a future spec.
- The proxy model does not introduce additional database tables or migrations.
- The menu entry for the map viewer is added to the existing `heat_flow/menus.py` (or a new `ghfdb/menus.py`) using the `flex_menu` pattern already established in the project.
