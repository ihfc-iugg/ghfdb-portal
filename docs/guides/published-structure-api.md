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

This guide covers `parents` today; `children` and `flat` get their own sections as they are built.

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

## Implementation notes

All three endpoints share one serializer builder, in `project/ghfdb/serializers.py`:
`published_fields()` builds a record's published columns from the column registry, reading each one
through `PublishedValueField` (a scalar) or `ConceptLabelsField` (a many-valued column) — the two
field classes behind the `null`/`[]` rendering above. A record serializer declares its non-published
keys, then appends `published_fields(...)` in `get_fields()`; `GHFDBParentSerializer` is the first
of the three.

The three viewsets share `GHFDBBaseViewSet`, in `project/ghfdb/viewsets.py`, which fixes the
published-identifier lookup and keeps the framework's own visibility filter.
`GHFDBParentViewSet` is the first concrete viewset built on it.
