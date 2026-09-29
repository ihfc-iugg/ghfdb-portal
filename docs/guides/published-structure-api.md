# The published structure through the API

The portal exposes the published Global Heat Flow Database itself, not only the portal's own data
model, as three read-only endpoints under `/api/v1/ghfdb/`:

- **`parents`** — one record per published parent heat flow value, one per site.
- **`children`** — one record per published determination, each carrying a link to its parent.
- **`flat`** — one row per determination, in the released file's own shape: every published parent
  column followed by every published child column, with the site's values repeated on every row
  that mentions it.

Every field name a record carries that is a published column is the published name exactly, in the
canonical published order — the same names and order the released database file itself uses. No
account is needed to read any of the three: the published database is public data, and every route
answers an unauthenticated request with the records it may show.

## Paging

Every list route is paged. `?page=<n>` selects a page, and `?page_size=<n>` sets how many records it
carries — 25 by default, 100 at the most. Asking for more than 100 is not refused; it is served at
100. Asking for a page past the last one is refused with `404 Not Found`, the same way a single
record that does not exist is.

A paged response carries the page's records under `results`, alongside `count` (how many records
exist in total), and `next` and `previous` (the adjacent pages' URLs, or `null` at either end):

```json
{
  "count": 138,
  "next": "https://portal.heatflow.world/api/v1/ghfdb/parents/?page=2",
  "previous": null,
  "results": [ ... ]
}
```

## Reading the whole database

An unauthenticated client is limited to 100 requests an hour. At the maximum page size, reading the
full published database — currently on the order of 90,000 determinations — takes on the order of
hours, not minutes, spread across enough requests to stay under that limit. A signed-in request is
limited to 1,000 an hour instead, which shortens that considerably, but every route still answers
with the same records either way — signing in changes nothing about what a request can see.

## Parents

`GET /api/v1/ghfdb/parents/` lists published parent heat flow values. `GET
/api/v1/ghfdb/parents/<ID_parent>/` returns one, addressed by its own published identifier.

Each record carries its own link, its two determination counts, and then every published parent
column, under its published name, in published order:

```
GET /api/v1/ghfdb/parents/?page_size=1
```

```json
{
  "count": 138,
  "next": "https://portal.heatflow.world/api/v1/ghfdb/parents/?page=2&page_size=1",
  "previous": null,
  "results": [
    {
      "url": "https://portal.heatflow.world/api/v1/ghfdb/parents/1/",
      "total_children": 4,
      "relevant_children": 3,
      "ID_parent": 1,
      "q": 70.5,
      "q_uncertainty": 5.2,
      "name": "Example Site",
      "lat_NS": 48.1234,
      "long_EW": 11.5678,
      "elevation": 512.0,
      "environment": "onshore_continental",
      "p_comment": null,
      "corr_HP_flag": false,
      "total_depth_MD": 500.0,
      "total_depth_TVD": 500.0,
      "explo_method": "borehole",
      "explo_purpose": ["Hydrocarbon", "Scientific"],
      "quality_parent": "good"
    }
  ]
}
```

`total_children` and `relevant_children` count every determination beneath the site, including one
the `children` endpoint does not list — an unpublished determination, or one whose dataset is not
public — so the counts can be larger than the number of determinations a consumer can actually read
through the API.

A published column the site holds no value for is still present on the record, empty rather than
missing — `null` for a column with no value, `[]` for a many-valued column with no members — so
every record's key set is identical.

Reading a single parent additionally carries `children` — the determinations belonging to that site,
in the same shape the `children` endpoint's list route carries them, and limited to the same records
a request to that endpoint could reach:

```
GET /api/v1/ghfdb/parents/1/
```

```json
{
  "url": "https://portal.heatflow.world/api/v1/ghfdb/parents/1/",
  "total_children": 1,
  "relevant_children": 1,
  "children": [
    {
      "url": "https://portal.heatflow.world/api/v1/ghfdb/children/11/",
      "parent": "https://portal.heatflow.world/api/v1/ghfdb/parents/1/",
      "lat_NS": 48.1234,
      "long_EW": 11.5678,
      "qc": 70.5,
      "qc_uncertainty": 5.2,
      "q_method": ["Bullard"],
      "...": "the rest of the published child columns, then ID"
    }
  ],
  "ID_parent": 1,
  "q": 70.5,
  "q_uncertainty": 5.2,
  "name": "Example Site",
  "lat_NS": 48.1234,
  "long_EW": 11.5678,
  "elevation": 512.0,
  "environment": "onshore_continental",
  "p_comment": null,
  "corr_HP_flag": false,
  "total_depth_MD": 500.0,
  "total_depth_TVD": 500.0,
  "explo_method": "borehole",
  "explo_purpose": ["Hydrocarbon", "Scientific"],
  "quality_parent": "good"
}
```

## Determinations

`GET /api/v1/ghfdb/children/` lists published heat-flow determinations. `GET
/api/v1/ghfdb/children/<ID>/` returns one, addressed by its own published identifier.

Each record on the list route carries its own link, a link to the parent it belongs to, the
coordinates of the site it was made at, and then every published child column, under its published
name, in published order, ending with `ID` — the determination's own published identifier:

```
GET /api/v1/ghfdb/children/?page_size=1
```

```json
{
  "count": 90214,
  "next": "https://portal.heatflow.world/api/v1/ghfdb/children/?page=2&page_size=1",
  "previous": null,
  "results": [
    {
      "url": "https://portal.heatflow.world/api/v1/ghfdb/children/11/",
      "parent": "https://portal.heatflow.world/api/v1/ghfdb/parents/1/",
      "lat_NS": 48.1234,
      "long_EW": 11.5678,
      "qc": 70.5,
      "qc_uncertainty": 5.2,
      "q_method": ["Bullard"],
      "q_top": 0.0,
      "q_bottom": 500.0,
      "probe_penetration": 3.5,
      "publication_reference": null,
      "data_reference": null,
      "relevant_child": true,
      "c_comment": null,
      "corr_IS_flag": "-",
      "corr_T_flag": "-",
      "corr_S_flag": "-",
      "corr_E_flag": "-",
      "corr_TOPO_flag": "-",
      "corr_PAL_flag": "-",
      "corr_SUR_flag": "-",
      "corr_CONV_flag": "-",
      "corr_HR_flag": "-",
      "expedition": null,
      "probe_type": [],
      "probe_length": null,
      "probe_tilt": null,
      "water_temperature": null,
      "geo_lithology": [],
      "geo_stratigraphy": [],
      "T_grad_mean": 25.0,
      "T_grad_uncertainty": null,
      "T_grad_mean_cor": null,
      "T_grad_uncertainty_cor": null,
      "T_method_top": [],
      "T_method_bottom": [],
      "T_shutin_top": null,
      "T_shutin_bottom": null,
      "T_corr_top": [],
      "T_corr_bottom": [],
      "T_number": null,
      "q_date": null,
      "tc_mean": 2.5,
      "tc_uncertainty": null,
      "tc_source": [],
      "tc_location": [],
      "tc_method": [],
      "tc_saturation": [],
      "tc_pT_conditions": [],
      "tc_pT_function": [],
      "tc_number": null,
      "tc_strategy": [],
      "Ref_IGSN": null,
      "quality_child": null,
      "ID": 11
    }
  ]
}
```

A method, lithology or thermal-conductivity metadata column that holds several values is a list of
them, not a joined string — `q_method` above carries one value, but two values would appear as
`["Bullard", "Interval"]`.

Reading a single determination carries the same keys, except `parent` is the full parent record — in
the shape the `parents` endpoint's own single-record route carries, but without that record's own
`children` — rather than a link to it, so a consumer following one request from a determination to
its parent never needs a second request to read the parent's own published columns:

```
GET /api/v1/ghfdb/children/11/
```

```json
{
  "url": "https://portal.heatflow.world/api/v1/ghfdb/children/11/",
  "parent": {
    "url": "https://portal.heatflow.world/api/v1/ghfdb/parents/1/",
    "total_children": 1,
    "relevant_children": 1,
    "ID_parent": 1,
    "q": 70.5,
    "q_uncertainty": 5.2,
    "name": "Example Site",
    "lat_NS": 48.1234,
    "long_EW": 11.5678,
    "elevation": 512.0,
    "environment": "onshore_continental",
    "p_comment": null,
    "corr_HP_flag": false,
    "total_depth_MD": 500.0,
    "total_depth_TVD": 500.0,
    "explo_method": "borehole",
    "explo_purpose": ["Hydrocarbon", "Scientific"],
    "quality_parent": "good"
  },
  "lat_NS": 48.1234,
  "long_EW": 11.5678,
  "qc": 70.5,
  "qc_uncertainty": 5.2,
  "q_method": ["Bullard"],
  "...": "the rest of the published child columns, then ID, exactly as the list route carries them"
}
```

A determination is served only where its parent is too — a determination whose site is in a dataset
that is not public, or whose parent carries no published identifier, is absent from both `children`
routes even if the determination's own dataset is public.

## Flat

`GET /api/v1/ghfdb/flat/` lists one row per published determination, in the released file's own
shape. `GET /api/v1/ghfdb/flat/<ID>/` returns one, addressed by its own published identifier.

Each row carries every published parent column, then every published child column, under their
published names, in published order, ending with `ID` — nothing else. A row carries no link, no
count, and no identifier belonging to the portal's own model.

A row does not distinguish which columns came from the parent's site and which came from the
determination itself — the parent's values are repeated on every row that shares them, the same way
a release file itself restates them, so two determinations at the same site carry the same `name`,
`lat_NS`, `explo_purpose` and every other parent column, once per row:

```
GET /api/v1/ghfdb/flat/?page_size=1
```

```json
{
  "count": 90214,
  "next": "https://portal.heatflow.world/api/v1/ghfdb/flat/?page=2&page_size=1",
  "previous": null,
  "results": [
    {
      "ID_parent": 1,
      "q": 70.5,
      "q_uncertainty": 5.2,
      "name": "Example Site",
      "lat_NS": 48.1234,
      "long_EW": 11.5678,
      "elevation": 512.0,
      "environment": "onshore_continental",
      "p_comment": null,
      "corr_HP_flag": false,
      "total_depth_MD": 500.0,
      "total_depth_TVD": 500.0,
      "explo_method": "borehole",
      "explo_purpose": ["Hydrocarbon", "Scientific"],
      "quality_parent": "good",
      "qc": 70.5,
      "qc_uncertainty": 5.2,
      "q_method": ["Bullard"],
      "q_top": 0.0,
      "q_bottom": 500.0,
      "probe_penetration": 3.5,
      "publication_reference": null,
      "data_reference": null,
      "relevant_child": true,
      "c_comment": null,
      "corr_IS_flag": "-",
      "corr_T_flag": "-",
      "corr_S_flag": "-",
      "corr_E_flag": "-",
      "corr_TOPO_flag": "-",
      "corr_PAL_flag": "-",
      "corr_SUR_flag": "-",
      "corr_CONV_flag": "-",
      "corr_HR_flag": "-",
      "expedition": null,
      "probe_type": [],
      "probe_length": null,
      "probe_tilt": null,
      "water_temperature": null,
      "geo_lithology": [],
      "geo_stratigraphy": [],
      "T_grad_mean": 25.0,
      "T_grad_uncertainty": null,
      "T_grad_mean_cor": null,
      "T_grad_uncertainty_cor": null,
      "T_method_top": [],
      "T_method_bottom": [],
      "T_shutin_top": null,
      "T_shutin_bottom": null,
      "T_corr_top": [],
      "T_corr_bottom": [],
      "T_number": null,
      "q_date": null,
      "tc_mean": 2.5,
      "tc_uncertainty": null,
      "tc_source": [],
      "tc_location": [],
      "tc_method": [],
      "tc_saturation": [],
      "tc_pT_conditions": [],
      "tc_pT_function": [],
      "tc_number": null,
      "tc_strategy": [],
      "Ref_IGSN": null,
      "quality_child": null,
      "ID": 11
    }
  ]
}
```

Reading a single row carries the same keys, in the same order, addressed by the determination's own
identifier rather than the parent's — `GET /api/v1/ghfdb/flat/11/` returns exactly the object the
list above carries at `results[0]`.

A row's columns follow the published release's own column order. Three columns a release file adds
beyond the portal's own data — the review status, the year, and the quality code a release's
assessment team supplies — are left out: the portal computes its own quality rather than storing a
supplied code, and the review status and year have no field in the portal's schema to read from.

A determination is served here under the same rule as `children`: only where its parent is served
too.

## Implementation notes

All three endpoints share one serializer builder, in `project/ghfdb/serializers.py`:
`published_fields()` builds a record's published columns from the column registry, reading each one
through `PublishedValueField` (a scalar) or `ConceptLabelsField` (a many-valued column) — the two
field classes behind the `null`/`[]` rendering above. A record serializer declares its non-published
keys, then appends `published_fields(...)` in `get_fields()`; `GHFDBParentSerializer` and
`GHFDBChildListSerializer` are two of the three. `GHFDBChildDetailSerializer` extends the list shape
with the nested parent record, and `GHFDBParentDetailSerializer` extends the parent shape with
`children`; each inserts its one extra field in `get_fields()` rather than declaring it as a class
attribute, where its name would collide with a name DRF already gives every field or serializer
(`Field.parent`, and the model's own `children` relation). `GHFDBFlatSerializer` is the third: it
declares no keys of its own, appending the parent columns, then the child columns, then `ID`, with
one override — `explo_purpose` reads through the determination's own interval rather than the site
directly, since the registry's own path to it only resolves on a parent record.

The three viewsets share `GHFDBBaseViewSet`, in `project/ghfdb/viewsets.py`, which fixes the
published-identifier lookup and keeps the framework's own visibility filter.
`GHFDBParentViewSet` and `GHFDBChildViewSet` are two of the three; each's single-record route
overrides `retrieve()` to load the nested record it carries. A determination is narrowed to parents
the parent route's own queryset serves to the requester, as a subquery, and a parent's attached
determinations are that same narrowed queryset filtered to the one parent, so `children` never
diverges from what a request to the `children` endpoint would itself return. `GHFDBFlatViewSet` is
the third viewset, and its own `get_queryset()` reuses `GHFDBChildViewSet`'s queryset rather than
restating that subquery, so `flat` never diverges from `children` either.
