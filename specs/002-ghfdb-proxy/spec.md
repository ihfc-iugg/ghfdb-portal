# Feature Specification: GHFDB Flat Data Interface

**Feature Branch**: `002-ghfdb-proxy`
**Created**: 2026-04-10
**Status**: Refined
**Refined**: 2026-04-14 — Added explicit GHFDB Child admin column order plus required search and filter fields for parent-level spreadsheet attributes.
**Refined**: 2026-04-17 — Replace single `GHFDB` proxy model with two distinct proxy models: `GHFDBChild` (backed by `HeatFlow`) and `GHFDBParent` (backed by `ParentHeatFlow`). Both registered to admin with spreadsheet-ordered list displays. Import/export resources attached to their respective model admin.
**Bugfix**: 2026-04-14 — [BUG-001] Added constrained-option behavior for `explo_purpose` admin filtering so list-filter choices are vocabulary-scoped.
**Bugfix**: 2026-04-17 — [BUG-002] Corrected the `GHFDBChild` admin changelist contract so it shows child-level fields first, with parent/site context columns retained only for orientation.
**Bugfix**: 2026-04-17 — [BUG-003] Clarified that child-admin queryset optimizations must use only valid ORM relation paths so changelist rendering cannot fail on invalid `prefetch_related()` lookups.
**Bugfix**: 2026-04-20 — [BUG-004] Broadened FR-015 vocabulary-scoping requirement to cover all concept-backed filter fields (`environment`, `explo_method`, `explo_purpose`) on both admins; added `_interval()` fallback safety requirement.
**References**: Fuchs et al. (2021); Fuchs et al. (2023); IHFC GHFDB v2024
**Input**: User description: "GHFDB product layer: proxy model, flat query interface, and web map viewer"
**Downstream**: Import/export pipeline is specified separately in `003-ghfdb-import-export`.

## Overview

This feature establishes the GHFDB flat data interface within the `project/ghfdb` app via **two complementary proxy models**:

- **`GHFDBChild`** — a proxy over `HeatFlow` with an optimised `GHFDBChildQuerySet` that returns all child-level GHFDB columns as a flat annotated structure (with optional parent-level data for a complete record) without N+1 queries. Registered in admin as "GHFDB Children". The `GHFDBChildImportResource` and `GHFDBExportResource` are attached to this admin.
- **`GHFDBParent`** — a proxy over `ParentHeatFlow` that retrieves parent-level data with optional children attached and supports queryset annotations for `total_children` (all child records linked to the parent) and `relevant_children` (child records that meet a quality or relevance threshold). Registered in admin as "GHFDB Parents". The `GHFDBParentImportResource` is attached to this admin.

The feature also delivers a dedicated "Explore" page that embeds the GHFDB web-map viewer inside a full-screen iframe with a main-menu link for easy access.

**Downstream feature**: Round-trip import/export utilities (staff-only admin, XLSX, vocabulary normalisation) are specified in `003-ghfdb-import-export`. That spec depends on the `GHFDBChild` proxy model and `GHFDBChildManager.for_export()` queryset produced by this spec.

**Out of scope (deferred):** Scheduled or automated release generation; public/anonymous downloadable exports.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - GHFDBChild Proxy Model for Efficient Flat Child Queries (Priority: P1)

A developer or data curator needs to query heat flow records in the exact flat structure used by the GHFDB spreadsheet product — one row per child heat-flow measurement along with all parent-site, thermal-gradient, and thermal-conductivity columns — without writing complex multi-join queries every time.

**Why this priority**: The child proxy model is the foundation that every other GHFDB product feature (export, admin display, API, map) depends on. Without a well-optimised flat view of the data, downstream features require duplicated query logic.

**Independent Test**: Can be tested independently by querying the proxy model and verifying that a single queryset call returns all expected GHFDB child-level columns without N+1 queries.

**Acceptance Scenarios**:

1. **Given** the database contains a `HeatFlow` record with linked site, parent, thermal-gradient, and thermal-conductivity data, **When** the `GHFDBChild` proxy queryset's `as_ghfdb_flat()` method is called, **Then** each record is returned as a flat structure containing all required GHFDB spreadsheet columns with no additional queries per row.
2. **Given** the `GHFDBChild` proxy model is used in the Django ORM, **When** standard queryset operations (filter, order_by, count) are applied, **Then** they behave identically to the underlying `HeatFlow` model.
3. **Given** the `GHFDBChild` proxy model, **When** accessed from the Django admin, **Then** it appears as a separate, read-oriented admin view labelled "GHFDB Children" with the `GHFDBChildImportResource` and `GHFDBExportResource` attached, and changelist queryset evaluation succeeds without invalid relation-path errors.
4. **Given** the GHFDB Children admin changelist, **When** a staff user views records, **Then** ~~the displayed columns are in this exact order: `ID_parent`, `q`, `q_uncertainty`, `name`, `lat_NS`, `long_EW`, `elevation`, `environment`, `corr_HP_flag`, `total_depth_MD`, `total_depth_TVD`, `explo_method`, `explo_purpose`, `country`, `region`, `continent`, `domain`~~ (superseded by BUG-002 because this duplicates the parent admin contract) and the displayed columns are in this exact order: `local_id`, `ID_parent`, `name`, `lat_NS`, `long_EW`, `qc`, `qc_uncertainty`, `q_method`, `q_top`, `q_bottom`, `probe_penetration`, `publication_reference`, `data_reference`, `relevant_child`, `c_comment`, `corr_IS_flag`, `corr_T_flag`, `corr_S_flag`, `corr_E_flag`, `corr_TOPO_flag`, `corr_PAL_flag`, `corr_SUR_flag`, `corr_CONV_flag`, `corr_HR_flag`, `expedition`, `probe_type`, `probe_length`, `probe_tilt`, `water_temperature`, `geo_lithology`, `geo_stratigraphy`, `T_grad_mean`, `T_grad_uncertainty`, `T_grad_mean_cor`, `T_grad_uncertainty_cor`, `T_method_top`, `T_method_bottom`, `T_shutin_top`, `T_shutin_bottom`, `T_corr_top`, `T_corr_bottom`, `T_number`, `q_date`, `tc_mean`, `tc_uncertainty`, `tc_source`, `tc_location`, `tc_method`, `tc_saturation`, `tc_pT_conditions`, `tc_pT_fuction`, `tc_number`, `tc_strategy`, `Ref_ISGN`.
5. **Given** the GHFDB Children admin changelist, **When** a staff user uses search and filters, **Then** search is supported by `name` and `ID_parent`, list filters are available for `environment`, `corr_HP_flag`, `explo_method`, `explo_purpose`, `country`, `region`, `continent`, and `domain`, and ~~`explo_purpose` filter choices are restricted to values accepted by the `HeatFlowSite.explo_purpose` vocabulary~~ (broadened by BUG-004) all concept-backed filter fields (`environment`, `explo_method`, `explo_purpose`) display vocabulary-scoped human-readable choices rather than raw stored keys.

---

### User Story 1b - GHFDBParent Proxy Model for Parent-Level Queries (Priority: P1)

A developer or data curator needs to query heat flow data at the **parent site level** — one row per parent site with aggregated child statistics — to support summary views, data quality dashboards, and parent-scoped import/export workflows.

**Why this priority**: The parent proxy model enables admin views and workflows that operate at the parent level (site-wide), which is distinct from the child-level flat export view. It also enables the `GHFDBParentImportResource` to be cleanly separated from the child import admin.

**Independent Test**: Can be tested independently by querying the proxy model and verifying that count annotations (`total_children`, `relevant_children`) are correct and return in a constant number of queries.

**Acceptance Scenarios**:

1. **Given** the database contains `ParentHeatFlow` records with linked child `HeatFlow` records, **When** the `GHFDBParent` queryset is called with count annotations, **Then** each record includes `total_children` (count of all linked `HeatFlow` children) and `relevant_children` (count meeting a quality/relevance threshold).
2. **Given** the `GHFDBParent` proxy model, **When** standard queryset operations (filter, order_by, count) are applied, **Then** they behave identically to the underlying `ParentHeatFlow` model.
3. **Given** the `GHFDBParent` proxy model, **When** accessed from the Django admin, **Then** it appears as a separate admin view labelled "GHFDB Parents" with the `GHFDBParentImportResource` attached.
4. **Given** the GHFDB Parents admin changelist, **When** a staff user views records, **Then** the displayed columns reflect the parent-level GHFDB spreadsheet columns in the correct order: `ID_parent`, `q`, `q_uncertainty`, `name`, `lat_NS`, `long_EW`, `elevation`, `environment`, `corr_HP_flag`, `total_depth_MD`, `total_depth_TVD`, `explo_method`, `explo_purpose`, `country`, `region`, `continent`, `domain`, plus `total_children` and `relevant_children` as computed columns.
5. **Given** the `GHFDBParent` queryset, **When** `with_children()` (or equivalent) is called, **Then** parent records are returned with their linked child data attached in a constant number of queries.

---

### Proxy Edge Cases

- What happens when a `HeatFlowCorrection` for a specific type doesn't exist for a given `HeatFlow` record? The correction subquery annotation returns `None` for that field.
- What happens when `thermal_gradient` or `thermal_conductivity` is `null` on a `HeatFlow` record? All related annotations return `None`; the queryset still returns the row without error.
- What happens when the map viewer iframe URL is unreachable? The page must degrade gracefully, showing an informative message rather than a blank frame.

### User Story 4 - Explore Map Viewer Page (Priority: P3)

A portal visitor wants a quick visual overview of the global heat flow distribution. They click a "Map" (or "Explore") link in the application's top navigation bar and see the GHFDB interactive web-map viewer embedded inside the portal page.

**Why this priority**: Lower priority than the data utilities since it is a UI convenience feature, but it is a direct user-facing deliverable that increases portal discoverability.

**Independent Test**: Can be tested independently by navigating to the map URL and confirming the iframe loads and the menu link is active, with no dependency on import/export functionality.

**Acceptance Scenarios**:

1. **Given** a logged-in or anonymous user, **When** they click the "Explore" menu item in the main navigation, **Then** they are taken to a portal page that renders the GHFDB web-map viewer inside a responsive, full-viewport iframe.
2. **Given** the map page, **When** it loads, **Then** no horizontal scrollbars appear and the iframe fills the available viewport height.
3. **Given** the main application menu, **When** the user is on the map page, **Then** the "Explore" menu item is marked as active/current.

---

### Map Edge Cases

- What happens when a `HeatFlowCorrection` for a specific type doesn't exist for a given `HeatFlow` record? The correction subquery annotation returns `None` for that field.
- What happens when `thermal_gradient` or `thermal_conductivity` is `null` on a `HeatFlow` record? All related annotations return `None`; the queryset still returns the row without error.
- What happens when the map viewer iframe URL is unreachable? The page must degrade gracefully, showing an informative message rather than a blank frame.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide two Django proxy models:
  - **`GHFDBChild`** backed by `HeatFlow` with a custom `GHFDBChildManager` and `GHFDBChildQuerySet` that returns all child-level GHFDB spreadsheet columns via an optimised single-query path (select_related and prefetch_related). Optional parent-level data may be included for a complete dataset.
  - **`GHFDBParent`** backed by `ParentHeatFlow` with a custom `GHFDBParentManager` and `GHFDBParentQuerySet` that retrieves parent-level data with optional children attached.
- **FR-002**: The `GHFDBChildQuerySet` MUST expose a named method (e.g., `as_ghfdb_flat()`) that annotates or selects all columns required by the GHFDB child-level output schema, with an option to include parent-level columns for a complete record.
- **FR-002b**: The `GHFDBParentQuerySet` MUST expose:
  - A method (e.g., `with_child_counts()`) that annotates each parent record with `total_children` (count of all linked `HeatFlow` children) and `relevant_children` (count of children meeting a quality or relevance threshold).
  - A method (e.g., `with_children()`) that prefetches or attaches linked child records in a constant number of queries.
- **FR-003 to FR-008**: Import/export pipeline behavior was split into `003-ghfdb-import-export`. This feature only defines the proxy/query/admin surface that those downstream resources attach to.
- **FR-009**: The system MUST provide a URL-accessible view at `ghfdb/explore/` (or equivalent) that renders an HTML template embedding the GHFDB web-map viewer (`https://ihfc-iugg.github.io/HeatFlowMapping/`) inside a full-screen iframe. The URL is hardcoded in the template.
- **FR-010**: A menu item labelled "Explore" (or equivalent) MUST be registered in the main application navigation bar pointing to the map viewer URL.
- **FR-011**: Both `GHFDBChild` and `GHFDBParent` proxy models MUST be registered with the Django admin (read-only mode is acceptable) so staff can inspect GHFDB-structured entries without modifying underlying normalised records.
- **FR-011b**: The `GHFDBChildImportResource` and `GHFDBExportResource` MUST be attached exclusively to the `GHFDBChild` admin. The `GHFDBParentImportResource` MUST be attached exclusively to the `GHFDBParent` admin. No import or export resource should be attached to both admins simultaneously.
- **FR-012**: The **`GHFDBChild`** admin changelist MUST ~~display these GHFDB spreadsheet fields in this exact order: `ID_parent`, `q`, `q_uncertainty`, `name`, `lat_NS`, `long_EW`, `elevation`, `environment`, `corr_HP_flag`, `total_depth_MD`, `total_depth_TVD`, `explo_method`, `explo_purpose`, `country`, `region`, `continent`, `domain`~~ (superseded by BUG-002 because those are parent-level summary columns) and MUST display the child-oriented changelist fields in this exact order: `local_id`, `ID_parent`, `name`, `lat_NS`, `long_EW`, `qc`, `qc_uncertainty`, `q_method`, `q_top`, `q_bottom`, `probe_penetration`, `publication_reference`, `data_reference`, `relevant_child`, `c_comment`, `corr_IS_flag`, `corr_T_flag`, `corr_S_flag`, `corr_E_flag`, `corr_TOPO_flag`, `corr_PAL_flag`, `corr_SUR_flag`, `corr_CONV_flag`, `corr_HR_flag`, `expedition`, `probe_type`, `probe_length`, `probe_tilt`, `water_temperature`, `geo_lithology`, `geo_stratigraphy`, `T_grad_mean`, `T_grad_uncertainty`, `T_grad_mean_cor`, `T_grad_uncertainty_cor`, `T_method_top`, `T_method_bottom`, `T_shutin_top`, `T_shutin_bottom`, `T_corr_top`, `T_corr_bottom`, `T_number`, `q_date`, `tc_mean`, `tc_uncertainty`, `tc_source`, `tc_location`, `tc_method`, `tc_saturation`, `tc_pT_conditions`, `tc_pT_fuction`, `tc_number`, `tc_strategy`, `Ref_ISGN`.
- **FR-012b**: The **`GHFDBParent`** admin changelist MUST display parent-level GHFDB spreadsheet columns in the same spreadsheet column order: `ID_parent`, `q`, `q_uncertainty`, `name`, `lat_NS`, `long_EW`, `elevation`, `environment`, `corr_HP_flag`, `total_depth_MD`, `total_depth_TVD`, `explo_method`, `explo_purpose`, `country`, `region`, `continent`, `domain`, followed by the computed columns `total_children` and `relevant_children`.
- **FR-013**: The **`GHFDBChild`** admin changelist MUST support text search on `name` and `ID_parent`. The **`GHFDBParent`** admin changelist MUST support text search on `name` and `ID_parent`.
- **FR-014**: The **`GHFDBChild`** admin changelist MUST provide filters for `environment`, `corr_HP_flag`, `explo_method`, `explo_purpose`, `country`, `region`, `continent`, and `domain`. The **`GHFDBParent`** admin changelist MUST provide the same set of filters.
- **FR-015**: For concept-backed admin list filters on both admins, filter options MUST be constrained to vocabulary-accepted values for the target field. ~~Specifically, the `explo_purpose` filter MUST only show values accepted by `HeatFlowSite.explo_purpose` and MUST NOT show unrelated `Concept` values.~~ (broadened by BUG-004) Specifically: the `environment` filter MUST show only values from the `GeographicEnvironment` vocabulary; the `explo_method` filter MUST show only values from the `ExplorationMethod` vocabulary; the `explo_purpose` filter MUST show only values from the `ExplorationPurpose` vocabulary. All three filters MUST display human-readable vocabulary labels, not raw stored concept keys. Each concept-backed filter on both the child and parent admins MUST use a vocabulary-scoped custom `SimpleListFilter` class.
- **FR-015b**: The `GHFDBChildAdmin._interval()` helper MUST return `None` (not the raw `Sample` object) when the `heatflowinterval` MTI accessor does not resolve, so that column display methods receive a correctly-typed value or `None`.
- **FR-016**: Before validating or mapping controlled-vocabulary spreadsheet values, the importer MUST normalise each token by removing surrounding square brackets (for example, `[Onshore (continental)]` -> `Onshore (continental)`) and converting the result to lowercase so standard GHFDB upload-template values remain compatible with lowercase vocabulary definitions.
- **FR-017**: `GHFDBChild` admin changelist queryset optimizations (`select_related`/`prefetch_related`) MUST reference only valid ORM relation paths on `HeatFlow` and linked models; invalid paths that cause changelist rendering errors are not permitted.

### Key Entities

- **GHFDBChild (proxy)**: A read-oriented proxy over `HeatFlow` that presents child heat-flow records in the flat GHFDB spreadsheet schema. Does not add database columns; adds custom manager (`GHFDBChildManager`) and queryset (`GHFDBChildQuerySet`) methods for efficient flat-data retrieval, including an `as_ghfdb_flat()` method for fully annotated single-query output and optional parent data inclusion. `verbose_name = "GHFDB Child"`, `verbose_name_plural = "GHFDB Children"`.
- **GHFDBParent (proxy)**: A read-oriented proxy over `ParentHeatFlow` that presents parent-site records in the GHFDB parent-column schema. Does not add database columns; adds custom manager (`GHFDBParentManager`) and queryset (`GHFDBParentQuerySet`) methods, including `with_child_counts()` (annotates `total_children` and `relevant_children`) and `with_children()` (prefetches linked child data). `verbose_name = "GHFDB Parent"`, `verbose_name_plural = "GHFDB Parents"`.
- **GHFDBParentImportResource**: The downstream parent import resource defined in `003-ghfdb-import-export`. In this feature it matters only as the resource attached to the **`GHFDBParent`** model admin.
- **GHFDBChildImportResource**: The downstream child import resource defined in `003-ghfdb-import-export`. In this feature it matters only as the resource attached to the **`GHFDBChild`** model admin.
- **GHFDBExportResource**: The downstream export resource defined in `003-ghfdb-import-export`. In this feature it matters only as the resource attached to the **`GHFDBChild`** model admin.
- **GHFDBExploreView**: A `TemplateView` subclass that renders the map viewer page. The iframe URL (`https://ihfc-iugg.github.io/HeatFlowMapping/`) is hardcoded directly in the template; no Django setting is required.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Querying all child records via `GHFDBChild.objects.as_ghfdb_flat()` executes in a constant number of database queries regardless of the number of records returned (no N+1 queries).
- **SC-002**: Querying parent records via `GHFDBParent.objects.with_child_counts()` returns correct `total_children` and `relevant_children` annotations in a constant number of database queries.
- **SC-003**: Both Django admin changelists render successfully for staff users with the exact required spreadsheet column order and the correct resource attachments (`GHFDBChildImportResource` + `GHFDBExportResource` on `GHFDBChild`; `GHFDBParentImportResource` on `GHFDBParent`).
- **SC-004**: The map viewer page loads and displays the iframe within 3 seconds on a standard broadband connection.
- **SC-005**: 100% of the parent-level and child-level spreadsheet columns required by this feature for admin inspection are exposed with no undocumented omissions, including the BUG-002 clarification that the child admin exposes the child-oriented column set while the parent admin retains the parent summary column set.

## Clarifications

### Session 2026-04-10

- Q: What is the default iframe URL for the map viewer, and should it be a configurable Django setting? → A: Hardcoded to `https://ihfc-iugg.github.io/HeatFlowMapping/` directly in the template. No Django setting required.

## Assumptions

- The official GHFDB spreadsheet column schema is defined by the Fuchs et al. (2023) publication and the `ghfdb_colmeta.json` metadata file already present in the codebase; no new column definitions will be introduced as part of this feature.
- The web-map viewer iframe URL (`https://ihfc-iugg.github.io/HeatFlowMapping/`) is hardcoded directly in the template; no Django setting is required.
- Import/export behavior is specified in `003-ghfdb-import-export`; this feature only defines the proxy/query/admin integration surface consumed by that downstream feature.
- The proxy model does not introduce additional database tables or migrations.
- The menu entry for the map viewer is added to the existing `heat_flow/menus.py` (or a new `ghfdb/menus.py`) using the `flex_menu` pattern already established in the project.
