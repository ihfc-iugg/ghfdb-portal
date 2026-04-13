# Data Model: GHFDB Import/Export Resource Classes

**Feature**: 002-ghfdb-product-utilities
**Date**: 2026-04-13
**Prerequisites**: [research.md](research.md) complete

## Overview

This document defines the class hierarchy, field mappings, and data flow for the GHFDB import/export system. The only schema change is the addition of `HeatFlow.local_id` to support upsert identification during import. All import/export logic operates on existing models with no additional tables.

## Proxy Model & Queryset Design

### GHFDB Proxy Model

| Attribute | Value |
|---|---|
| **Extends** | `HeatFlow` (proxy, no new table) |
| **`verbose_name`** | `"GHFDB Entry"` |
| **`verbose_name_plural`** | `"GHFDB Entries"` |
| **`objects`** | `GHFDBManager` (provides `as_ghfdb_flat()` and `for_export()`) |

### HeatFlow — New Field: `local_id`

| Field | Type | Constraints | Purpose |
|---|---|---|---|
| `local_id` | `CharField(max_length=255)` | `null=True`, `blank=True`, `db_index=True` | Stores the GHFDB spreadsheet `ID` column; enables `import_id_fields = ("local_id",)` for upsert |

**Migration required**: Yes — adds a nullable varchar column to the `heat_flow_heatflow` table.

### GHFDBQuerySet Methods

| Method | DB Queries | Purpose |
|---|---|---|
| `as_ghfdb_flat()` | 1–2 (constant) | Annotated flat queryset for admin list, filtering, API |
| `for_export()` | ~16 (constant) | `as_ghfdb_flat()` + prefetch_related for all ~15 M2M relations |

### Annotation Name Mapping (used by `as_ghfdb_flat()`)

#### Scalar Annotations (folded into main SELECT with JOINs)

| Annotation Name | ORM Path | GHFDB Column |
|---|---|---|
| `site_name` | `sample__sample__name` | `name` |
| `lat_ns` | `sample__sample__location__y` | `lat_NS` |
| `long_ew` | `sample__sample__location__x` | `long_EW` |
| `site_elevation` | `sample__sample__elevation` | `elevation` |
| `site_environment` | `sample__sample__environment` | `environment` |
| `site_explo_method` | `sample__sample__explo_method` | `explo_method` |
| `site_country` | `sample__sample__country` | `Country` |
| `site_region` | `sample__sample__region` | `Region` |
| `site_continent` | `sample__sample__continent` | `Continent` |
| `site_domain` | `sample__sample__domain` | `Domain` |
| `total_depth_md` | `sample__sample__length` | `total_depth_MD` |
| `total_depth_tvd` | `sample__sample__vertical_depth` | `total_depth_TVD` |
| `p_q` | `parent__value` | `q` |
| `p_q_uncertainty` | `parent__uncertainty` | `q_uncertainty` |
| `p_corr_hp_flag` | `parent__corr_HP_flag` | `corr_HP_flag` |
| `p_comment` | `parent__comment` | `p_comment` |
| `interval_top` | `sample__top` | `q_top` |
| `interval_bottom` | `sample__bottom` | `q_bottom` |
| `tgrad_value` | `thermal_gradient__value` | `T_grad_mean` |
| `tgrad_uncertainty` | `thermal_gradient__uncertainty` | `T_grad_uncertainty` |
| `tgrad_corrected` | `thermal_gradient__corrected_value` | `T_grad_mean_cor` |
| `tgrad_corrected_unc` | `thermal_gradient__corrected_uncertainty` | `T_grad_uncertainty_cor` |
| `tgrad_shutin_top` | `thermal_gradient__shutin_top` | `T_shutin_top` |
| `tgrad_shutin_bottom` | `thermal_gradient__shutin_bottom` | `T_shutin_bottom` |
| `tgrad_number` | `thermal_gradient__number` | `T_number` |
| `tc_value` | `thermal_conductivity__value` | `tc_mean` |
| `tc_uncertainty` | `thermal_conductivity__uncertainty` | `tc_uncertainty` |
| `tc_number` | `thermal_conductivity__number` | `tc_number` |
| `probe_penetration` | `sample__probe_metadata__penetration` | `probe_penetration` |
| `probe_length` | `sample__probe_metadata__length` | `probe_length` |
| `probe_tilt` | `sample__probe_metadata__tilt` | `probe_tilt` |

#### Subquery Annotations (correction flags, one correlated subquery each)

| Annotation Name | Source | GHFDB Column |
|---|---|---|
| `corr_IS_flag` | `HeatFlowCorrection(type=IS).status` | `corr_IS_flag` |
| `corr_T_flag` | `HeatFlowCorrection(type=T).status` | `corr_T_flag` |
| `corr_S_flag` | `HeatFlowCorrection(type=S).status` | `corr_S_flag` |
| `corr_E_flag` | `HeatFlowCorrection(type=E).status` | `corr_E_flag` |
| `corr_TOPO_flag` | `HeatFlowCorrection(type=TOPO).status` | `corr_TOPO_flag` |
| `corr_PAL_flag` | `HeatFlowCorrection(type=PAL).status` | `corr_PAL_flag` |
| `corr_SUR_flag` | `HeatFlowCorrection(type=SUR).status` | `corr_SUR_flag` |
| `corr_CONV_flag` | `HeatFlowCorrection(type=CONV).status` | `corr_CONV_flag` |
| `corr_HR_flag` | `HeatFlowCorrection(type=HR).status` | `corr_HR_flag` |

#### Prefetch Paths (M2M fields, one query each for `for_export()`)

| Prefetch Path | GHFDB Column |
|---|---|
| `method` | `q_method` |
| `sample__sample__explo_purpose` | `explo_purpose` |
| `thermal_gradient__method_top` | `T_method_top` |
| `thermal_gradient__method_bottom` | `T_method_bottom` |
| `thermal_gradient__correction_top` | `T_corr_top` |
| `thermal_gradient__correction_bottom` | `T_corr_bottom` |
| `thermal_conductivity__source` | `tc_source` |
| `thermal_conductivity__location` | `tc_location` |
| `thermal_conductivity__method` | `tc_method` |
| `thermal_conductivity__saturation` | `tc_saturation` |
| `thermal_conductivity__pT_conditions` | `tc_pT_conditions` |
| `thermal_conductivity__pT_function` | `tc_pT_function` |
| `thermal_conductivity__strategy` | `tc_strategy` |
| `sample__probe_metadata__probe_type` | `probe_type` |

## Entity Relationship Summary

```
GHFDB Spreadsheet (flat, ~60 columns per row)
    │
    ├── Parent Import Resource ──► ParentHeatFlow ──► HeatFlowSite ──► Point (location)
    │                                                    │
    │                                                    ├── explo_purpose (M2M)
    │                                                    └── geographic fields
    │
    └── Child Import Resource  ──► HeatFlow ──► HeatFlowInterval
                                     │              │
                                     ├── parent (FK to ParentHeatFlow)
                                     ├── thermal_gradient (FK) ──► ThermalGradient
                                     │                                  ├── method_top (M2M)
                                     │                                  ├── method_bottom (M2M)
                                     │                                  ├── correction_top (M2M)
                                     │                                  └── correction_bottom (M2M)
                                     ├── thermal_conductivity (FK) ──► IntervalConductivity
                                     │                                      ├── source (M2M)
                                     │                                      ├── location (M2M)
                                     │                                      ├── method (M2M)
                                     │                                      ├── saturation (M2M)
                                     │                                      ├── pT_conditions (M2M)
                                     │                                      ├── pT_function (M2M)
                                     │                                      └── strategy (M2M)
                                     ├── method (M2M)
                                     └── corrections ──► HeatFlowCorrection (9 types)
                                                              └── ProbeMetadata (1:1 on interval)
```

## Module: `_base.py` — Shared Constants & Format

### GHFDBImportFormat

```python
class GHFDBImportFormat(XLSX):
    """Custom XLSX reader for the GHFDB spreadsheet template.

    The official template has:
    - Rows 1–5: metadata (title, description, version)
    - Row 6: technical column headers
    - Row 7: human-readable descriptions
    - Row 8+: data rows
    - Sheet name: "data list"
    """
```

### Column Order Constants

```python
# Ordered list of all GHFDB spreadsheet column names
# Matches the official template column order (Fuchs et al. 2023)
GHFDB_COLUMN_ORDER: list[str] = [
    # Parent (P01–P13)
    "ID_parent", "q", "q_uncertainty", "name", "lat_NS", "long_EW",
    "elevation", "environment", "p_comment", "corr_HP_flag",
    "total_depth_MD", "total_depth_TVD", "explo_method", "explo_purpose",
    "Country", "Region", "Continent", "Domain",
    # Child measurement (C01–C49)
    "ID", "qc", "qc_uncertainty", "q_method", "q_top", "q_bottom",
    "probe_penetration", "relevant_child", "c_comment",
    # Corrections (C11–C19)
    "corr_IS_flag", "corr_T_flag", "corr_S_flag", "corr_E_flag",
    "corr_TOPO_flag", "corr_PAL_flag", "corr_SUR_flag", "corr_CONV_flag",
    "corr_HR_flag",
    # Probe metadata (C20–C24)
    "expedition", "probe_type", "probe_length", "probe_tilt",
    "water_temperature",
    # Thermal gradient (C27–C37)
    "T_grad_mean", "T_grad_uncertainty", "T_grad_mean_cor",
    "T_grad_uncertainty_cor", "T_method_top", "T_method_bottom",
    "T_shutin_top", "T_shutin_bottom", "T_corr_top", "T_corr_bottom",
    "T_number",
    # Thermal conductivity (C39–C48)
    "tc_mean", "tc_uncertainty", "tc_source", "tc_location",
    "tc_method", "tc_saturation", "tc_pT_conditions", "tc_pT_function",
    "tc_number", "tc_strategy",
    # References
    "q_date",
]

# Columns that belong to parent-level import
PARENT_COLUMNS: list[str] = [
    "ID_parent", "q", "q_uncertainty", "name", "lat_NS", "long_EW",
    "elevation", "environment", "p_comment", "corr_HP_flag",
    "total_depth_MD", "total_depth_TVD", "explo_method", "explo_purpose",
    "Country", "Region", "Continent", "Domain",
]

# Correction column → HeatFlowCorrection.correction_type mapping
CORRECTION_COL_MAP: dict[str, str] = {
    "corr_IS_flag": "IS",
    "corr_T_flag": "T",
    "corr_S_flag": "S",
    "corr_E_flag": "E",
    "corr_TOPO_flag": "TOPO",
    "corr_PAL_flag": "PAL",
    "corr_SUR_flag": "SUR",
    "corr_CONV_flag": "CONV",
    "corr_HR_flag": "HR",
}
```

---

## Module: `_widgets.py` — Custom Import/Export Widgets

### Widget Hierarchy

```
import_export.widgets.Widget
├── ConceptWidget          # Single research_vocabs Concept (case-insensitive label lookup)
├── MultiConceptWidget     # Semicolon-separated Concepts
├── QuantityWidget         # Pint Quantity ↔ plain numeric
├── YesNoWidget            # "Yes"/"No" ↔ Boolean
└── RelatedModelWidget     # Creates/updates related model from multiple row columns
    ├── ParentWidget       # Creates HeatFlowSite + ParentHeatFlow location from parent columns
    ├── IntervalWidget     # Creates HeatFlowInterval from depth columns
    ├── GradientWidget     # Creates ThermalGradient from gradient columns
    └── ConductivityWidget # Creates IntervalConductivity from conductivity columns
```

### ConceptWidget

| Aspect | Detail |
|--------|--------|
| **Purpose** | Map a single human-readable label to a `research_vocabs.Concept` instance |
| **Import** | `clean(value, row)` → case-insensitive label lookup with vocabulary cache |
| **Export** | `render(value)` → `str(concept)` (label) |
| **Error** | `ValueError` with invalid value + list of valid labels |
| **Cache** | Built once per import run; `{label.lower(): Concept}` dict |

### MultiConceptWidget

| Aspect | Detail |
|--------|--------|
| **Purpose** | Map semicolon-separated labels to a list of Concepts |
| **Import** | `clean(value, row)` → split by `;`, validate each via `ConceptWidget`, return list |
| **Export** | `render(value)` → `"; ".join(concept labels)` |
| **Error** | Collects all invalid values, raises single `ValueError` listing them all |
| **Separator** | `";"` (configurable, default matches GHFDB convention) |

### QuantityWidget

| Aspect | Detail |
|--------|--------|
| **Purpose** | Convert between plain numerics and Pint Quantity values |
| **Import** | `clean(value, row)` → `Quantity(Decimal(value), unit)` |
| **Export** | `render(value)` → `value.magnitude` (strips unit) |
| **Unit** | Fixed per field instance (e.g., `"mW/m²"`, `"K/km"`, `"W/(m·K)"`) |

### YesNoWidget

| Aspect | Detail |
|--------|--------|
| **Purpose** | Convert "Yes"/"No" strings to Boolean |
| **Import** | `clean(value, row)` → `True` for "yes"/"1"/True; `False` for "no"/"0"/False; `None` for empty |
| **Export** | `render(value)` → `"Yes"` / `"No"` / `""` |

### RelatedModelWidget (base)

| Aspect | Detail |
|--------|--------|
| **Purpose** | Create/update a related model instance from multiple spreadsheet columns |
| **Constructor** | `model`, `field_map`, `m2m_map`, `sentinel_column`, `widget_map` |
| **`field_map`** | `Dict[str, str]` — spreadsheet column → model field name (scalar fields) |
| **`m2m_map`** | `Dict[str, Tuple[str, MultiConceptWidget]]` — spreadsheet column → (model M2M field, widget) |
| **`widget_map`** | `Dict[str, Widget]` — model field → widget for cleaning individual values |
| **`sentinel_column`** | If this column is empty, return `None` (skip creation) |
| **Import flow** | 1. Check sentinel → 2. Extract & clean scalar fields → 3. `full_clean()` → 4. `save()` → 5. Store M2M for deferred set |
| **Error handling** | `ValidationError` from `full_clean()` → `ValueError` prefixed with model name |
| **Lifecycle** | New instance per row; M2M set via `set_m2m_relations()` called from resource |

---

## Module: `parent.py` — GHFDBParentImportResource

### Class Definition

```python
class GHFDBParentImportResource(ModelResource):
    """Import resource for GHFDB parent-level data.

    Target model: ParentHeatFlow
    Upsert key: local_id (from spreadsheet ID_parent)

    Creates/updates:
    - ParentHeatFlow (value, uncertainty, comment, corr_HP_flag)
    - HeatFlowSite (via RelatedModelWidget on 'sample' FK)
    - Point (location, via ParentWidget)
    """

    class Meta:
        model = ParentHeatFlow
        import_id_fields = ("local_id",)
        fields = (
            "local_id",      # ID_parent → ParentHeatFlow.local_id
            "value",         # q → ParentHeatFlow.value
            "uncertainty",   # q_uncertainty → ParentHeatFlow.uncertainty
            "comment",       # p_comment → ParentHeatFlow.comment
            "corr_HP_flag",  # corr_HP_flag → ParentHeatFlow.corr_HP_flag
            "sample",        # FK → HeatFlowSite (created via ParentWidget)
        )
        use_transactions = True
        rollback_on_validation_errors = True
        clean_model_instances = True
        store_instance = True
```

### Field Declarations

| Resource Field | Spreadsheet Column | Widget | Target |
|---|---|---|---|
| `local_id` | `ID_parent` | `CharWidget` | `ParentHeatFlow.local_id` |
| `value` | `q` | `QuantityWidget("mW/m²")` | `ParentHeatFlow.value` |
| `uncertainty` | `q_uncertainty` | `QuantityWidget("mW/m²")` | `ParentHeatFlow.uncertainty` |
| `comment` | `p_comment` | `CharWidget` | `ParentHeatFlow.comment` |
| `corr_HP_flag` | `corr_HP_flag` | `YesNoWidget` | `ParentHeatFlow.corr_HP_flag` |
| `sample` | *(multiple columns)* | `ParentWidget` | `ParentHeatFlow.sample` (FK to HeatFlowSite) |

### ParentWidget — RelatedModelWidget for HeatFlowSite

```python
ParentWidget(
    model=HeatFlowSite,
    sentinel_column="name",  # Site must have a name
    field_map={
        "name": "name",
        "lat_NS": "location.y",      # Special handling: creates/updates Point
        "long_EW": "location.x",     # Special handling: creates/updates Point
        "elevation": "elevation",
        "environment": "environment",
        "explo_method": "explo_method",
        "total_depth_MD": "length",
        "total_depth_TVD": "vertical_depth",
        "Country": "country",
        "Region": "region",
        "Continent": "continent",
        "Domain": "domain",
    },
    m2m_map={
        "explo_purpose": ("explo_purpose", MultiConceptWidget(vocabularies.ExplorationPurpose())),
    },
    widget_map={
        "elevation": QuantityWidget("m"),
        "length": QuantityWidget("m"),
        "vertical_depth": QuantityWidget("m"),
        "environment": ConceptWidget(vocabularies.GeographicEnvironment()),
        "explo_method": ConceptWidget(vocabularies.ExplorationMethod()),
    },
)
```

### `before_import()` — Parent Deduplication

```python
def before_import(self, dataset, **kwargs):
    """Deduplicate rows by ID_parent — keep first occurrence per parent."""
    seen = set()
    rows_to_keep = []
    id_parent_col = dataset.headers.index("ID_parent")

    for i, row in enumerate(dataset):
        id_parent = row[id_parent_col]
        if id_parent not in seen:
            seen.add(id_parent)
            rows_to_keep.append(row)

    # Replace dataset with deduplicated rows
    new_dataset = tablib.Dataset(headers=dataset.headers)
    for row in rows_to_keep:
        new_dataset.append(row)

    # Swap dataset contents
    dataset.wipe()
    for row in new_dataset:
        dataset.append(row)

    super().before_import(dataset, **kwargs)
```

---

## Module: `child.py` — GHFDBChildImportResource

### Class Definition

```python
class GHFDBChildImportResource(ModelResource):
    """Import resource for GHFDB child-level measurement data.

    Target model: HeatFlow
    Upsert key: local_id (from spreadsheet ID)

    Creates/updates:
    - HeatFlow (value, uncertainty, method, date, expedition, comments)
    - HeatFlowInterval (via RelatedModelWidget)
    - ThermalGradient (via RelatedModelWidget, optional)
    - IntervalConductivity (via RelatedModelWidget, optional)
    - ProbeMetadata (via after_save_instance, optional)
    - HeatFlowCorrection × 9 (via after_save_instance)
    """

    class Meta:
        model = HeatFlow
        import_id_fields = ("local_id",)
        fields = (
            "local_id",             # ID → HeatFlow.local_id
            "value",                # qc → HeatFlow.value
            "uncertainty",          # qc_uncertainty → HeatFlow.uncertainty
            "date_acquired",        # q_date → HeatFlow.date_acquired
            "expedition",           # expedition → HeatFlow.expedition
            "water_temperature",    # water_temperature → HeatFlow.water_temperature
            "c_comment",            # c_comment → HeatFlow.c_comment
            "is_relevant",          # relevant_child → HeatFlow.is_relevant
            "parent",              # FK to ParentHeatFlow (looked up by ID_parent)
            "sample",              # FK to HeatFlowInterval (created via IntervalWidget)
            "thermal_gradient",    # FK to ThermalGradient (created via GradientWidget)
            "thermal_conductivity", # FK to IntervalConductivity (created via ConductivityWidget)
            "method",              # M2M → handled via MultiConceptWidget
        )
        use_transactions = True
        rollback_on_validation_errors = True
        clean_model_instances = True
        store_instance = True
        skip_unchanged = False
```

### Field Declarations

| Resource Field | Spreadsheet Column(s) | Widget | Target |
|---|---|---|---|
| `local_id` | `ID` | `CharWidget` | `HeatFlow.local_id` |
| `value` | `qc` | `QuantityWidget("mW/m²")` | `HeatFlow.value` |
| `uncertainty` | `qc_uncertainty` | `QuantityWidget("mW/m²")` | `HeatFlow.uncertainty` |
| `method` | `q_method` | `MultiConceptWidget(HeatFlowMethod)` | `HeatFlow.method` (M2M) |
| `date_acquired` | `q_date` | `CharWidget` | `HeatFlow.date_acquired` |
| `expedition` | `expedition` | `CharWidget` | `HeatFlow.expedition` |
| `water_temperature` | `water_temperature` | `QuantityWidget("°C")` | `HeatFlow.water_temperature` |
| `c_comment` | `c_comment` | `CharWidget` | `HeatFlow.c_comment` |
| `is_relevant` | `relevant_child` | `YesNoWidget` | `HeatFlow.is_relevant` |
| `parent` | `ID_parent` | `ForeignKeyWidget(ParentHeatFlow, "local_id")` | `HeatFlow.parent` FK |
| `sample` | `q_top`, `q_bottom`, `geo_lithology`, `geo_stratigraphy` | `IntervalWidget` | `HeatFlow.sample` FK |
| `thermal_gradient` | `T_grad_*` columns (11 cols) | `GradientWidget` | `HeatFlow.thermal_gradient` FK |
| `thermal_conductivity` | `tc_*` columns (10 cols) | `ConductivityWidget` | `HeatFlow.thermal_conductivity` FK |

### IntervalWidget — RelatedModelWidget for HeatFlowInterval

```python
IntervalWidget(
    model=HeatFlowInterval,
    sentinel_column=None,  # Always create (every child has an interval)
    field_map={
        "q_top": "top",
        "q_bottom": "bottom",
    },
    m2m_map={
        "geo_lithology": ("lithology", MultiConceptWidget(...)),
        "geo_stratigraphy": ("stratigraphy", MultiConceptWidget(...)),
    },
    widget_map={
        "top": QuantityWidget("m"),
        "bottom": QuantityWidget("m"),
    },
)
```

**Note**: The `HeatFlowInterval.sample` FK (pointing to the site) is set by the resource in `before_import_row()` by looking up the `ParentHeatFlow` via `ID_parent` and using its `sample` (HeatFlowSite).

### GradientWidget — RelatedModelWidget for ThermalGradient

```python
GradientWidget(
    model=ThermalGradient,
    sentinel_column="T_grad_mean",  # Only create if gradient data is present
    field_map={
        "T_grad_mean": "value",
        "T_grad_uncertainty": "uncertainty",
        "T_grad_mean_cor": "corrected_value",
        "T_grad_uncertainty_cor": "corrected_uncertainty",
        "T_shutin_top": "shutin_top",
        "T_shutin_bottom": "shutin_bottom",
        "T_number": "number",
    },
    m2m_map={
        "T_method_top": ("method_top", MultiConceptWidget(vocabularies.TemperatureMethod())),
        "T_method_bottom": ("method_bottom", MultiConceptWidget(vocabularies.TemperatureMethod())),
        "T_corr_top": ("correction_top", MultiConceptWidget(vocabularies.TemperatureCorrection())),
        "T_corr_bottom": ("correction_bottom", MultiConceptWidget(vocabularies.TemperatureCorrection())),
    },
    widget_map={
        "value": QuantityWidget("K/km"),
        "uncertainty": QuantityWidget("K/km"),
        "corrected_value": QuantityWidget("K/km"),
        "corrected_uncertainty": QuantityWidget("K/km"),
        "shutin_top": QuantityWidget("hr"),
        "shutin_bottom": QuantityWidget("hr"),
    },
)
```

### ConductivityWidget — RelatedModelWidget for IntervalConductivity

```python
ConductivityWidget(
    model=IntervalConductivity,
    sentinel_column="tc_mean",  # Only create if conductivity data is present
    field_map={
        "tc_mean": "value",
        "tc_uncertainty": "uncertainty",
        "tc_number": "number",
    },
    m2m_map={
        "tc_source": ("source", MultiConceptWidget(vocabularies.ConductivitySource())),
        "tc_location": ("location", MultiConceptWidget(vocabularies.ConductivityLocation())),
        "tc_method": ("method", MultiConceptWidget(vocabularies.ConductivityMethod())),
        "tc_saturation": ("saturation", MultiConceptWidget(vocabularies.ConductivitySaturation())),
        "tc_pT_conditions": ("pT_conditions", MultiConceptWidget(vocabularies.ConductivityPTConditions())),
        "tc_pT_function": ("pT_function", MultiConceptWidget(vocabularies.ConductivityPTFunction())),
        "tc_strategy": ("strategy", MultiConceptWidget(vocabularies.ConductivityStrategy())),
    },
    widget_map={
        "value": QuantityWidget("W/(m·K)"),
        "uncertainty": QuantityWidget("W/(m·K)"),
    },
)
```

### `after_save_instance()` — Corrections & Probe Metadata

```python
def after_save_instance(self, instance, row, **kwargs):
    """Create HeatFlowCorrection + ProbeMetadata after HeatFlow is saved."""

    # 1. Corrections (9 types)
    status_map = {s.label.lower(): s.value for s in HeatFlowCorrection.StatusChoices}
    for col, corr_type in CORRECTION_COL_MAP.items():
        raw = row.get(col)
        if raw:
            status_key = str(raw).strip().lower()
            if status_key not in status_map:
                raise ValidationError({col: f"Invalid correction status '{raw}'"})
            HeatFlowCorrection.objects.update_or_create(
                heat_flow=instance,
                correction_type=corr_type,
                defaults={"status": status_map[status_key]},
            )

    # 2. Probe metadata (if any probe columns are non-empty)
    interval = instance.sample  # HeatFlowInterval
    probe_data = {
        "penetration": row.get("probe_penetration"),
        "length": row.get("probe_length"),
        "tilt": row.get("probe_tilt"),
    }
    probe_m2m = {"probe_type": row.get("probe_type")}

    if any(v for v in probe_data.values()):
        probe, _ = ProbeMetadata.objects.update_or_create(
            interval=interval,
            defaults={k: v for k, v in probe_data.items() if v is not None},
        )
        if probe_m2m.get("probe_type"):
            # Clean via MultiConceptWidget and set
            ...

    # 3. Set M2M on related models created by widgets
    for field_name in ("sample", "thermal_gradient", "thermal_conductivity"):
        widget = self.fields[field_name].widget
        if hasattr(widget, 'set_m2m_relations'):
            related_instance = getattr(instance, field_name)
            if related_instance:
                widget.set_m2m_relations(related_instance)
```

---

## Module: `export.py` — GHFDBExportResource

### Class Definition

```python
class GHFDBExportResource(ModelResource):
    """Export resource that produces a GHFDB-format XLSX from HeatFlow data.

    Uses the GHFDBQuerySet.for_export() queryset which provides:
    - as_ghfdb_flat() annotations for all scalar/FK fields
    - prefetch_related for all M2M fields
    """

    class Meta:
        model = GHFDB  # Proxy model
        export_order = GHFDB_COLUMN_ORDER
        # All fields are declared explicitly — no introspection
```

### Field Declarations (simplified)

Each GHFDB column has an explicit `Field` declaration. Examples:

| Export Field | Column Name | Source | Render Logic |
|---|---|---|---|
| `ID_parent` | `ID_parent` | `parent.local_id` | `dehydrate` → `str` |
| `q` | `q` | annotation `p_q` | `dehydrate` → magnitude |
| `q_uncertainty` | `q_uncertainty` | annotation `p_q_uncertainty` | magnitude |
| `name` | `name` | annotation `site_name` | str |
| `lat_NS` | `lat_NS` | annotation `lat_ns` | Decimal |
| `long_EW` | `long_EW` | annotation `long_ew` | Decimal |
| `q_method` | `q_method` | prefetch `method` M2M | `"; ".join(labels)` |
| `corr_IS_flag` | `corr_IS_flag` | annotation `corr_IS_flag` | status label |
| `T_grad_mean` | `T_grad_mean` | annotation `tgrad_value` | magnitude |
| `tc_source` | `tc_source` | prefetch `thermal_conductivity.source` | `"; ".join(labels)` |

### `get_queryset()`

```python
def get_queryset(self):
    return GHFDB.objects.for_export()
```

---

## Admin Integration

### GHFDBAdmin (modified)

```python
class GHFDBAdmin(ImportExportMixin, admin.ModelAdmin):
    """Admin for the GHFDB proxy model with import/export support.

    Import: Staff selects between Site or Child resource.
    Export: Single export resource produces full GHFDB XLSX.
    """

    def get_import_resource_classes(self):
        return [GHFDBParentImportResource, GHFDBChildImportResource]

    def get_export_resource_classes(self):
        return [GHFDBExportResource]

    def get_import_formats(self):
        return [GHFDBImportFormat]

    def get_export_formats(self):
        return [XLSX]
```

### Admin Workflow

```
┌─────────────────────────────────────────────────┐
│  Django Admin: GHFDB Entries                    │
│                                                 │
│  [Import]  [Export]                              │
│                                                 │
│  Import:                                        │
│    1. Upload GHFDB XLSX                          │
│    2. Select resource: ▼                         │
│       ├── GHFDB Parent                          │
│       └── GHFDB Child                           │
│    3. Preview → Confirm                          │
│                                                 │
│  Export:                                        │
│    1. Apply filters (optional)                   │
│    2. Click Export → XLSX download               │
└─────────────────────────────────────────────────┘
```

---

## Data Flow Diagrams

### Import: Parent-Level

```
GHFDB XLSX  ──┬── before_import(): deduplicate by ID_parent
              │
              ├── For each unique ID_parent row:
              │     ├── ParentWidget.clean():
              │     │     ├── Extract name, lat, lon, elevation, environment, etc.
              │     │     ├── Create/get Point(x=lon, y=lat)
              │     │     ├── Create/update HeatFlowSite
              │     │     ├── full_clean() validation
              │     │     └── Return HeatFlowSite instance
              │     │
              │     ├── ParentHeatFlow fields:
              │     │     ├── value ← q (QuantityWidget)
              │     │     ├── uncertainty ← q_uncertainty (QuantityWidget)
              │     │     ├── comment ← p_comment (CharWidget)
              │     │     ├── corr_HP_flag ← corr_HP_flag (YesNoWidget)
              │     │     └── local_id ← ID_parent (CharWidget)
              │     │
              │     ├── save ParentHeatFlow (upsert on local_id)
              │     │
              │     └── after_save_instance():
              │           └── ParentWidget.set_m2m_relations():
              │                 └── site.explo_purpose.set(concepts)
              │
              └── Result: All ParentHeatFlows + HeatFlowSites created/updated
```

### Import: Child-Level

```
GHFDB XLSX  ──┬── For each row:
              │     ├── parent ← ForeignKeyWidget(ParentHeatFlow, "local_id")
              │     │     └── Looks up ParentHeatFlow by ID_parent
              │     │
              │     ├── IntervalWidget.clean():
              │     │     ├── Extract q_top, q_bottom
              │     │     ├── Create HeatFlowInterval
              │     │     ├── Set interval.sample = parent.sample (HeatFlowSite)
              │     │     └── Return HeatFlowInterval instance
              │     │
              │     ├── GradientWidget.clean():
              │     │     ├── Check sentinel: T_grad_mean non-empty?
              │     │     ├── If yes: create ThermalGradient with all T_grad_* fields
              │     │     └── If no: return None
              │     │
              │     ├── ConductivityWidget.clean():
              │     │     ├── Check sentinel: tc_mean non-empty?
              │     │     ├── If yes: create IntervalConductivity with all tc_* fields
              │     │     └── If no: return None
              │     │
              │     ├── HeatFlow fields:
              │     │     ├── value ← qc (QuantityWidget)
              │     │     ├── method ← q_method (MultiConceptWidget)
              │     │     └── ... remaining child fields
              │     │
              │     ├── save HeatFlow (upsert on local_id)
              │     │
              │     └── after_save_instance():
              │           ├── Create/update 9 HeatFlowCorrections
              │           ├── Create/update ProbeMetadata (if present)
              │           └── Set M2M on interval, gradient, conductivity
              │
              └── Result: All HeatFlows + related records created/updated
```
