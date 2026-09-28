# Research — 006 published structure API

Findings the plan rests on, read from the code on `main` at 720f559.

## R1 — Where the endpoints register

The framework's router is the public `fairdm_api_router` in `fairdm/api/router.py`, a
`DefaultRouter` mounted under `/api/v1/` by `fairdm/api/urls.py`, which `fairdm.conf.urls` includes
at `api/` with the namespace `api`. Everything registered on it appears in the API index and in the
drf-spectacular schema at `/api/v1/schema/`, with Swagger and ReDoc pages beside it.

Two constraints decide where our registration call lives:

- The router caches its URL list the first time `urls` is read, so a registration must happen
  before `fairdm.api.urls` is imported.
- Importing `fairdm.api.router` registers every sample and measurement type in the framework's
  registry at import time. Importing it from an `AppConfig.ready()` that runs before `heat_flow`
  has registered its types would silently drop those types from the API.

`config/urls.py` includes `project.ghfdb.urls` before `fairdm.conf.urls`, and both run after every
app is ready. Registering from `project/ghfdb/urls.py` satisfies both constraints without new
machinery. Prefixes: `ghfdb/parents`, `ghfdb/children`, `ghfdb/flat`, so the routes are
`/api/v1/ghfdb/parents/` and so on, and their URL names are `api:ghfdb-parents-list` and
`api:ghfdb-parents-detail` (and the same for the other two).

## R2 — Import path of the application

The app's `name` is `project.ghfdb` and its models load as `project.ghfdb.models`. Any new module
must import its siblings relatively or as `project.ghfdb.*`. Importing `ghfdb.models` loads the
proxy models a second time under another module name, and Django refuses the duplicate.

## R3 — What the framework applies by default

From `fairdm/api/settings.py`:

| Setting | Default | Consequence here |
|---|---|---|
| Permission | `FairDMObjectPermissions` | reads allowed with no credentials; writes need a login, and a read-only viewset has no write routes, so a write is refused either way |
| Pagination | `FairDMPagination` | `page`, `page_size`, default 25, maximum 100; a page past the end is a 404 |
| Throttle | anonymous 100/hour, authenticated 1000/hour | inherited unchanged |
| Filter backends | `FairDMVisibilityFilter`, `DjangoFilterBackend`, `OrderingFilter` | see R4 |
| Renderer | orjson, plus the browsable API | a Pint quantity cannot be rendered, see R5 |

## R4 — Visibility and ordering

`FairDMVisibilityFilter` restricts a measurement queryset to records in a public dataset for an
anonymous request, and adds the records a signed-in user holds a view permission on. The proxies
scope to records carrying a published identifier. The two are complementary: the proxy says a
record belongs to the published database, the visibility filter says its dataset may be shown. A
record in a private dataset is not served to an anonymous consumer even if it carries an identifier.

`OrderingFilter` with no `ordering_fields` offers ordering on every serializer field whose source
is not `*`, which would include the many-valued columns. Ordering on a many-to-many path repeats a
row once per related value, so a page would carry duplicates. The spec keeps filtering and ordering
out of scope, so the viewsets keep the visibility filter and drop the other two backends. Pages are
ordered by published identifier, then primary key, so a page is stable.

## R5 — Values the renderer cannot take as stored

Quantity fields come back from an `F()` annotation as Pint quantities. The export resource already
converts them to a plain magnitude (`_mag` in `resources/export.py`), but it returns `""` for a
missing value, which is the spreadsheet's convention. The API emits `null` for a missing scalar and
`[]` for a many-valued column with no members (spec D7), so it needs its own conversion rather than
the export's.

The two columns nothing resolves (`publication_reference`, `data_reference`) are annotated as
`Value("")`. An empty string and a missing value are the same thing to a consumer here, so both are
emitted as `null`.

## R6 — The column registry

`project/ghfdb/columns.py::PublishedColumns.ENTRIES` maps every published parent and child column
to a group (scalar or many-valued) and an accessor. `PARENT_COLUMNS` and `CHILD_COLUMNS` in
`constants.py` give the order. Serializers are built from those two, never from a restated list.

Two accessors are written for one context and do not hold in another:

- `explo_purpose` reads `sample.heatflowsite.explo_purpose`, which is right on a parent (whose
  sample is the site) and wrong on a determination (whose sample is the interval). On a flat row the
  path is `sample.heatflowinterval.site.explo_purpose`, which `for_export()` already prefetches.
- `quality_parent` is annotated on the parent queryset but not on the child queryset, so a flat row
  cannot read it today. `as_ghfdb_flat()` on the child queryset gains `quality_parent` from
  `parent__quality`.

The serializer builder takes a per-context override map for exactly these, rather than a second
registry.

## R7 — Query cost

- Parent list: `as_ghfdb_flat()` plus `with_child_counts()` is one query, plus one prefetch for
  exploration purposes, plus the paginator's count. Constant.
- Determination list and flat rows: `for_export()` is 18 queries, measured and documented in
  `managers.py`, plus the count. Constant.
- Parent detail with its determinations attached, and determination detail with its parent nested:
  one extra annotated query each for the related side. Constant.

Each story's tests assert that the query count for a page of one record equals the count for a
page of several.

## R8 — Identifier uniqueness

Neither `ParentHeatFlow.ghfdb_id` nor `HeatFlow.ghfdb_id` is unique in the database. Both import
resources upsert on it (`import_id_fields`), so a duplicate cannot arise through an import, but the
database does not forbid one. A single-record route that matched two records would raise
`MultipleObjectsReturned` and answer with a server error. The detail routes resolve a duplicate to
the earliest record by primary key rather than failing, and the flat and determination lists carry
both rows as they are.

A non-numeric identifier never reaches the view: the route's lookup pattern is digits only, so it
is a 404 from the resolver.

## R9 — Child counts count published determinations

`with_child_counts()` counts every child of a parent, including a determination with no published
identifier (possible since ADR-0014: a determination without an identifier is its row). The
proxies exclude such a determination everywhere else, so a parent would report more determinations
than a consumer can reach through its attached list. The proxy is by definition the published view,
so both counts are narrowed to children carrying a published identifier. The admin's parent list
reads the same annotation and becomes consistent with its own child list as a result.

## R10 — The disputed column vocabulary (#122)

`decisions.md` requires planning to check which disputed names these responses would expose.
Issue #122 disputes three things:

1. Metadata in `ghfdb_colmeta.json` for `ID_parent`, `quality_parent`, `Ref_IGSN`, `quality_child`,
   `Quality_Code_Child`, `Quality_Score_Parent`. That is metadata, not names.
2. Resource declarations for 25 columns. Resolved on `main` since: every published column has a
   `PublishedColumns` entry.
3. The child queryset's annotation key for site elevation, `elevation` against `site_elevation`.
   That is an internal key. The published column is `elevation` either way, and the API reads the
   published name through the column registry.

None of the three changes a published column name, so no story is gated on #122. `Ref_IGSN`
carries a comment recommending its removal. Removing it would remove the key from these responses,
which the registry-driven serializers follow without a code change here.

## R11 — The flat row and the determination's own identifier

The published release carries an `ID` column, the determination's own identifier, which the portal
stores as `HeatFlow.ghfdb_id`. `constants.py` holds it in `META_FIELDS`, not `CHILD_COLUMNS`. The
spec defines the flat row as every published parent column followed by every published child
column in the order `constants.py` holds, and SC-006 bounds every key to that set plus four named
additions. The flat row therefore does not carry `ID`. A consumer reaches a single row by it (the
route is addressed by it), and every flat row carries `ID_parent`.

## R12 — FR-009 and the released row

FR-009 asks every record on a list route to carry a link to its own route. FR-010 and US3 scenario
2 say a flat row carries published columns and nothing else, naming links explicitly. The specific
rule governs the general one: a flat row carries no link, and FR-009 holds on the parent and
determination routes.
