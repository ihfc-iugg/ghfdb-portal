# GHFDB Field Mapping

This page documents how each field of the community-defined **Global Heat Flow Database structure** relates to tables in the underlying **relational database** and their corresponding **Django models**.

The GHFDB spreadsheet is designed for human readability and ease of data entry, using a single table to represent a variety of concepts—ranging from site-level metadata to specific measurement records. This leads to an incorrect conclusion that all data belongs to a single logical structure within the database. In reality, however, these fields originate from different database tables and models, linked through foreign keys and object relationships defined in Django.

Below is a mapping table that clarifies how each field in the GHFDB spreadsheet corresponds to the actual database tables and Django models used in the FairDM framework. Use this table if you wish to understand how to access specific data using the Django ORM or if you simply wish to understand the underlying structure of the GHFDB data as it is stored in the database.

## Column Descriptions

| Column Name | Description |
| --- | --- |
| **GHFDB Name** | The original field name as it appears in the GHFDB spreadsheet (e.g., `q`, `lat_NS`, `elevation`). |
| **Database Table** | The name of the actual database table where the data is stored (e.g., `heat_flow_surfaceheatflow`). This reflects the low-level storage destination. |
| **Accessed From** | The Django model used to access the value (e.g., `SurfaceHeatFlow`, `HeatFlowSite`). This is typically the model from which a queryset would be created. |
| **Accessor** | The Django field name or property used to retrieve the value from the model listed in "Accessed From" (e.g., `value`, `x`, `name`). This can be a direct model field or a related field through a foreign key. |
| **Declared By** | The model where the field is originally declared. This is important when `Accessed From` accesses the field via a related object or mixin (e.g., `fairdm.location.Point`, `fairdm.core.Sample`). |

<!-- TODO: add automated mapping test when import/export spec is implemented -->

## Mapping Table

Fields are grouped by the database model they belong to, following the normalised relational structure.
The GHFDB spreadsheet column name (e.g. `q`, `tc_mean`) is the key for cross-referencing with the
[GHFDB specification](https://doi.org/10.5194/essd-14-2553-2022).

### Site-level Fields (P01–P13) — HeatFlowSite & ParentHeatFlow

`ParentHeatFlow` is the aggregated, quality-controlled heat flow value for a site.
It was previously named `SurfaceHeatFlow` in older versions of this codebase.

| GHFDB Name | GHFDB Ref | Database Table | Accessed From | Accessor | Declared By |
| --- | --- | --- | --- | --- | --- |
| q | P01 | heat\_flow\_parentheatflow | ParentHeatFlow | value | ParentHeatFlow |
| q\_uncertainty | P02 | heat\_flow\_parentheatflow | ParentHeatFlow | uncertainty | ParentHeatFlow |
| name | P03 | fairdm\_sample | HeatFlowSite | name | fairdm.core.Sample |
| lat\_NS | P04 | fairdm\_point | HeatFlowSite | location.y | fairdm.location.Point |
| long\_EW | P05 | fairdm\_point | HeatFlowSite | location.x | fairdm.location.Point |
| elevation | P06 | heat\_flow\_heatflowsite | HeatFlowSite | elevation | HeatFlowSite |
| environment | P07 | heat\_flow\_heatflowsite | HeatFlowSite | environment | HeatFlowSite |
| p\_comment | P08 | heat\_flow\_parentheatflow | ParentHeatFlow | comment | ParentHeatFlow |
| corr\_HP\_flag | P09 | heat\_flow\_parentheatflow | ParentHeatFlow | corr\_HP\_flag | ParentHeatFlow |
| total\_depth\_MD | P10 | heat\_flow\_heatflowsite | HeatFlowSite | length | fairdm\_geo.GenericHole |
| total\_depth\_TVD | P11 | heat\_flow\_heatflowsite | HeatFlowSite | vertical\_depth | fairdm\_geo.GeoDepthInterval |
| explo\_method | P12 | heat\_flow\_heatflowsite | HeatFlowSite | explo\_method | HeatFlowSite |
| explo\_purpose | P13 | heat\_flow\_heatflowsite | HeatFlowSite | explo\_purpose | HeatFlowSite |
| Country | — | heat\_flow\_heatflowsite | HeatFlowSite | country | HeatFlowSite |
| Region | — | heat\_flow\_heatflowsite | HeatFlowSite | region | HeatFlowSite |
| Continent | — | heat\_flow\_heatflowsite | HeatFlowSite | continent | HeatFlowSite |
| Domain | — | heat\_flow\_heatflowsite | HeatFlowSite | domain | HeatFlowSite |

### Child-level Fields (C01–C49)

#### HeatFlow (child interval heat flow determination)

| GHFDB Name | GHFDB Ref | Database Table | Accessed From | Accessor | Declared By |
| --- | --- | --- | --- | --- | --- |
| qc | C01 | heat\_flow\_heatflow | HeatFlow | value | HeatFlow |
| qc\_uncertainty | C02 | heat\_flow\_heatflow | HeatFlow | uncertainty | HeatFlow |
| q\_method | C03 | heat\_flow\_heatflow | HeatFlow | method | HeatFlow |
| ID | — | heat\_flow\_heatflow | HeatFlow | local\_id | HeatFlow |
| relevant\_child | C09 | heat\_flow\_heatflow | HeatFlow | is\_relevant | HeatFlow |
| c\_comment | C10 | heat\_flow\_heatflow | HeatFlow | c\_comment | HeatFlow |
| expedition | C20 | heat\_flow\_heatflow | HeatFlow | expedition | HeatFlow |
| water\_temperature | C24 | heat\_flow\_heatflow | HeatFlow | water\_temperature | HeatFlow |
| q\_date | C38 | heat\_flow\_heatflow | HeatFlow | date\_acquired | HeatFlow |

#### HeatFlowInterval (depth interval within the borehole)

An interval belongs to a site through `HeatFlowInterval.site`, a foreign key to `HeatFlowSite`.
The site's own fields are reached from a child heat flow as
`sample__heatflowinterval__site__<field>`.

| GHFDB Name | GHFDB Ref | Database Table | Accessed From | Accessor | Declared By |
| --- | --- | --- | --- | --- | --- |
| q\_top | C04 | heat\_flow\_heatflowinterval | HeatFlowInterval | top | fairdm\_geo.GeoDepthInterval |
| q\_bottom | C05 | heat\_flow\_heatflowinterval | HeatFlowInterval | bottom | fairdm\_geo.GeoDepthInterval |
| geo\_lithology | C25 | heat\_flow\_heatflowinterval | HeatFlowInterval | lithology | fairdm\_geo.GeoDepthInterval |
| geo\_stratigraphy | C26 | heat\_flow\_heatflowinterval | HeatFlowInterval | stratigraphy | fairdm\_geo.GeoDepthInterval |

#### HeatFlowCorrection (per-disturbance correction flags — C11–C19)

Correction flags are no longer stored as direct Boolean fields on `HeatFlow`.
Each flag is a separate `HeatFlowCorrection` record accessed via `heat_flow.corrections.filter(correction_type=<TYPE>)`.

| GHFDB Name | GHFDB Ref | Database Table | Accessed From | Accessor | Declared By |
| --- | --- | --- | --- | --- | --- |
| corr\_IS\_flag | C11 | heat\_flow\_heatflowcorrection | HeatFlowCorrection | status (type=IS) | HeatFlowCorrection |
| corr\_T\_flag | C12 | heat\_flow\_heatflowcorrection | HeatFlowCorrection | status (type=T) | HeatFlowCorrection |
| corr\_S\_flag | C13 | heat\_flow\_heatflowcorrection | HeatFlowCorrection | status (type=S) | HeatFlowCorrection |
| corr\_E\_flag | C14 | heat\_flow\_heatflowcorrection | HeatFlowCorrection | status (type=E) | HeatFlowCorrection |
| corr\_TOPO\_flag | C15 | heat\_flow\_heatflowcorrection | HeatFlowCorrection | status (type=TOPO) | HeatFlowCorrection |
| corr\_PAL\_flag | C16 | heat\_flow\_heatflowcorrection | HeatFlowCorrection | status (type=PAL) | HeatFlowCorrection |
| corr\_SUR\_flag | C17 | heat\_flow\_heatflowcorrection | HeatFlowCorrection | status (type=SUR) | HeatFlowCorrection |
| corr\_CONV\_flag | C18 | heat\_flow\_heatflowcorrection | HeatFlowCorrection | status (type=CONV) | HeatFlowCorrection |
| corr\_HR\_flag | C19 | heat\_flow\_heatflowcorrection | HeatFlowCorrection | status (type=HR) | HeatFlowCorrection |

#### ProbeMetadata (marine probe instrument parameters — C06, C21–C23)

Probe instrument fields were previously stored directly on `HeatFlow`. They are now on a
separate `ProbeMetadata` model linked via a `OneToOneField` to `HeatFlowInterval`.
Access pattern: `heat_flow.sample.probe_metadata.<field>`.

| GHFDB Name | GHFDB Ref | Database Table | Accessed From | Accessor | Declared By |
| --- | --- | --- | --- | --- | --- |
| probe\_penetration | C06 | heat\_flow\_probemetadata | ProbeMetadata | penetration | ProbeMetadata |
| probe\_type | C21 | heat\_flow\_probemetadata | ProbeMetadata | probe\_type | ProbeMetadata |
| probe\_length | C22 | heat\_flow\_probemetadata | ProbeMetadata | length | ProbeMetadata |
| probe\_tilt | C23 | heat\_flow\_probemetadata | ProbeMetadata | tilt | ProbeMetadata |

#### ThermalGradient (C27–C37)

| GHFDB Name | GHFDB Ref | Database Table | Accessed From | Accessor | Declared By |
| --- | --- | --- | --- | --- | --- |
| T\_grad\_mean | C27 | heat\_flow\_thermalgradient | ThermalGradient | value | ThermalGradient |
| T\_grad\_uncertainty | C28 | heat\_flow\_thermalgradient | ThermalGradient | uncertainty | ThermalGradient |
| T\_grad\_mean\_cor | C29 | heat\_flow\_thermalgradient | ThermalGradient | corrected\_value | ThermalGradient |
| T\_grad\_uncertainty\_cor | C30 | heat\_flow\_thermalgradient | ThermalGradient | corrected\_uncertainty | ThermalGradient |
| T\_method\_top | C31 | heat\_flow\_thermalgradient | ThermalGradient | method\_top | ThermalGradient |
| T\_method\_bottom | C32 | heat\_flow\_thermalgradient | ThermalGradient | method\_bottom | ThermalGradient |
| T\_shutin\_top | C33 | heat\_flow\_thermalgradient | ThermalGradient | shutin\_top | ThermalGradient |
| T\_shutin\_bottom | C34 | heat\_flow\_thermalgradient | ThermalGradient | shutin\_bottom | ThermalGradient |
| T\_corr\_top | C35 | heat\_flow\_thermalgradient | ThermalGradient | correction\_top | ThermalGradient |
| T\_corr\_bottom | C36 | heat\_flow\_thermalgradient | ThermalGradient | correction\_bottom | ThermalGradient |
| T\_number | C37 | heat\_flow\_thermalgradient | ThermalGradient | number | ThermalGradient |

#### IntervalConductivity (C39–C48)

| GHFDB Name | GHFDB Ref | Database Table | Accessed From | Accessor | Declared By |
| --- | --- | --- | --- | --- | --- |
| tc\_mean | C39 | heat\_flow\_intervalconductivity | IntervalConductivity | value | IntervalConductivity |
| tc\_uncertainty | C40 | heat\_flow\_intervalconductivity | IntervalConductivity | uncertainty | IntervalConductivity |
| tc\_source | C41 | heat\_flow\_intervalconductivity | IntervalConductivity | source | IntervalConductivity |
| tc\_location | C42 | heat\_flow\_intervalconductivity | IntervalConductivity | location | IntervalConductivity |
| tc\_method | C43 | heat\_flow\_intervalconductivity | IntervalConductivity | method | IntervalConductivity |
| tc\_saturation | C44 | heat\_flow\_intervalconductivity | IntervalConductivity | saturation | IntervalConductivity |
| tc\_pT\_conditions | C45 | heat\_flow\_intervalconductivity | IntervalConductivity | pT\_conditions | IntervalConductivity |
| tc\_pT\_function | C46 | heat\_flow\_intervalconductivity | IntervalConductivity | pT\_function | IntervalConductivity |
| tc\_number | C47 | heat\_flow\_intervalconductivity | IntervalConductivity | number | IntervalConductivity |
| tc\_strategy | C48 | heat\_flow\_intervalconductivity | IntervalConductivity | strategy | IntervalConductivity |

#### References & Review

| GHFDB Name | GHFDB Ref | Database Table | Accessed From | Accessor | Declared By |
| --- | --- | --- | --- | --- | --- |
| publication\_reference | C07 | fairdm\_dataset | Dataset | related\_literature | fairdm.core.Dataset |
| data\_reference | C08 | fairdm\_dataset | Dataset | reference | fairdm.core.Dataset |
| Reviewer\_name | — | heat\_flow\_review | Review | name | Review |
| Reviewer\_comment | — | heat\_flow\_review | Review | comment | Review |
| Review\_date | — | heat\_flow\_review | Review | completion\_date | Review |

#### Removed Fields

The following fields existed in older versions of the data model but have been removed or relocated.

| GHFDB Name | GHFDB Ref | Old Location | Reason Removed | Current Mapping |
| --- | --- | --- | --- | --- |
| Ref\_ISGN | C49 | HeatFlow.IGSN | IGSN identifies the physical *sample*, not the heat flow *measurement*; belongs on the Sample subclass | `HeatFlowSite.identifiers` / `HeatFlowInterval.identifiers` via FairDM generic identifier relationship |
| probe\_penetration | C06 | HeatFlow.probe\_penetration | Probe instrument parameters belong on the interval, not the heat flow measurement | `ProbeMetadata.penetration` (see above) |
| probe\_length | C22 | HeatFlow.probe\_length | Same rationale as probe\_penetration | `ProbeMetadata.length` (see above) |
| probe\_tilt | C23 | HeatFlow.probe\_tilt | Same rationale as probe\_penetration | `ProbeMetadata.tilt` (see above) |
| probe\_type | C21 | HeatFlow.probe\_type | Same rationale as probe\_penetration | `ProbeMetadata.probe_type` (see above) |
| relevant\_child | C09 | HeatFlow.relevant\_child | Renamed for clarity | `HeatFlow.is_relevant` |
| corr\_IS\_flag through corr\_HR\_flag | C11–C19 | HeatFlow.corr\_\*\_flag (Boolean) | Booleans cannot encode correction severity/status; normalised to `HeatFlowCorrection` records | `HeatFlowCorrection(correction_type=<TYPE>).status` |

## HeatFlow ghfdb_id

`HeatFlow.ghfdb_id` is the stable upsert key for GHFDB child imports.

- Type: `PositiveIntegerField`
- Constraints: `null=True`, `blank=True`, `db_index=True`
- Source column: GHFDB spreadsheet `ID`
- Import usage: `GHFDBChildImportResource.Meta.import_id_fields = ("ghfdb_id",)`

> **Note:** The GHFDB spreadsheet uses string-format IDs (e.g. `R24-001588`). Parsing these
> strings into the stored integer is handled by the import resource layer (see import/export spec).

For parent imports, the corresponding stable key is `ParentHeatFlow.ghfdb_id`, mapped from
spreadsheet `ID_parent` (e.g. `R24-P000004`).

## Proxy Model Access Patterns

The product layer now uses two proxy models:

- `GHFDBChild` (proxy over `HeatFlow`) for child-row flat/export workflows
- `GHFDBParent` (proxy over `ParentHeatFlow`) for parent-level summary workflows

### GHFDBChild

`GHFDBChild` exposes flattened spreadsheet-like child columns through annotated queryset helpers.

- Flat annotated queryset: `GHFDBChild.objects.as_ghfdb_flat()`
- Export-ready queryset with prefetches: `GHFDBChild.objects.for_export()`

The annotation names are the published column names, so a flat row can be read with the
spreadsheet in hand. Two exceptions carry a `site_` prefix because the bare name would collide
with a field the measurement already has:

- Child values: `qc`, `qc_uncertainty`, `relevant_child`, `q_date`, `ID_parent`
- Site and location: `site_name`, `lat_NS`, `long_EW`, `elevation`, `environment`,
  `explo_method`, `site_country`, `site_region`, `site_continent`, `site_domain`,
  `total_depth_MD`, `total_depth_TVD`
- Parent values: `q`, `q_uncertainty`, `corr_HP_flag`, `p_comment`
- Interval: `q_top`, `q_bottom`
- Thermal gradient: `T_grad_mean`, `T_grad_uncertainty`, `T_grad_mean_cor`,
  `T_grad_uncertainty_cor`, `T_shutin_top`, `T_shutin_bottom`, `T_number`
- Conductivity: `tc_mean`, `tc_uncertainty`, `tc_number`
- Probe: `probe_penetration`, `probe_length`, `probe_tilt`
- Corrections: `corr_IS_flag`, `corr_T_flag`, `corr_S_flag`, `corr_E_flag`, `corr_TOPO_flag`, `corr_PAL_flag`, `corr_SUR_flag`, `corr_CONV_flag`, `corr_HR_flag`

### GHFDBParent

`GHFDBParent` provides parent-level helpers for child aggregation and parent-scoped admin workflows.

- Parent queryset with computed child counts: `GHFDBParent.objects.with_child_counts()`
  - Adds `total_children`: all linked `HeatFlow` children
  - Adds `relevant_children`: linked children where `is_relevant=True`
- Parent queryset with prefetched children: `GHFDBParent.objects.with_children()`

Admin registration split:

- `GHFDBChildAdmin` (model: `GHFDBChild`) has `GHFDBChildImportResource` and `GHFDBExportResource`
- `GHFDBParentAdmin` (model: `GHFDBParent`) has `GHFDBParentImportResource` only

## Large Export Limits

The synchronous XLSX export path is currently validated for up to approximately 50,000 rows.

- `GHFDBExportResource.get_queryset()` should remain memory-conscious and avoid materializing full result sets eagerly.
- For exports beyond the tested synchronous limit, move the job to a background task (deferred to a future specification).
