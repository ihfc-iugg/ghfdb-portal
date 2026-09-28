# Implementation Plan: The published structure reachable through the API

**Branch**: `006-published-structure-api` | **Date**: 2026-09-29 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/006-published-structure-api/spec.md`

## Summary

Three read-only viewsets over the two proxy models in `project/ghfdb/models.py`, registered on the
framework's router: parents, determinations (`children`), and the released row (`flat`). Their
serializers are built from the column registry (`PublishedColumns` in `project/ghfdb/columns.py`)
and the column order in `project/ghfdb/constants.py`, so no column list is restated. Querysets come
from the proxy managers, which already annotate every scalar column and prefetch every many-valued
one in a constant number of queries.

The work is almost all new code in `project/ghfdb/`: `serializers.py` grows, `viewsets.py` is new,
and `urls.py` registers the three. One small change lands in `managers.py`: the child queryset gains
`quality_parent`, which the released row needs. A consumer guide lands in `docs/guides/`.

## Technical Context

**Language/Version**: Python 3.13, Django 5.2

**Primary Dependencies**: FairDM (router, pagination, permissions, visibility filter), Django REST
Framework, drf-spectacular. No new dependency.

**Storage**: PostgreSQL. No schema change and no migration.

**Testing**: pytest, pytest-django, factory-boy through `tests/factories.py`. Tests mirror the source
module they exercise, grouped in `Test<Subject>` classes, per
`docs/contributing/standards/testing.md`.

**Target Platform**: Linux server, JSON over HTTP

**Project Type**: Django web application

**Performance Goals**: the query count behind one page does not change with the number of records
on it (FR-018, SC-003).

**Constraints**: read-only; no credentials needed; nothing outside the published database, on any
route.

**Scale/Scope**: the portal holds a sample of the database today. The full release is roughly
90,000 determinations. The query count per page is constant by design. The time the parent page's
count aggregate takes at that size is not measured here (D17).

## Constitution Check

*GATE: passed before research, re-checked after the design below.*

| Article | Bearing on this feature | Verdict |
|---|---|---|
| I. Testing | Every task writes its failing test first. Query-count invariance is asserted, not assumed. | Conforms |
| II. Simplicity | One serializer builder over the existing registry. No new abstraction layer, no second column list. | Conforms |
| III. Anti-Abstraction | DRF's own viewset, serializer and field classes, with the minimum subclassing each context needs. | Conforms |
| IV. Integration-First | Endpoints are tested through real HTTP requests against the real router and schema view. | Conforms |
| V. Security & data-safety | Read-only routes, the framework's visibility filter kept, non-numeric identifiers refused at the resolver. | Conforms |
| VI. Documentation | Each story documents its endpoint in the consumer guide in the same story. | Conforms, own tasks |
| VIII. Internationalization | Schema summaries and descriptions use `gettext_lazy`. | Conforms |
| XI. FAIR-First Scientific Data | The published structure becomes machine-accessible with no account. | Advances it |
| XII. GHFDB Schema Fidelity | Published names, casing and order come from `constants.py` and `columns.py` directly, with the ADR-0003 corrections. | Advances it |
| XIII. FairDM-First Integration | Registered on the framework's router, paged and permissioned by the framework's classes. | Conforms |
| XV. Spec-Driven Workflow | This plan follows an approved specification. | Conforms |

No violations to justify.

## Design

### Serializer builder (US1, reused by US2 and US3)

In `project/ghfdb/serializers.py`:

- `PublishedValueField` — a read-only field for a scalar published column. `None` and `""` render
  as `null`. A Pint quantity renders as its float magnitude. Anything else passes through.
- `ConceptLabelsField` — a read-only field for a many-valued column. It reads a related manager by
  a dotted source and renders `[concept.label, ...]` from `.all()`, so it uses the prefetch cache. A
  `None` anywhere on the path renders `[]`.
- `published_fields(columns, overrides=None)` — returns an ordered mapping of published name to
  field for the given column list, reading each column's group and accessor from
  `PublishedColumns.ENTRIES`. `overrides` replaces the accessor for a named column in contexts
  where the registry's accessor does not hold (research R6).

Each record serializer overrides `get_fields()` to return its non-published keys first, then
`published_fields(...)`, which satisfies FR-003 by construction. drf-spectacular reads `get_fields()`
so the schema follows. The field classes carry `extend_schema_field` hints (a nullable scalar, an
array of strings) so the schema describes their types.

### Parents (US1)

- Record keys: `url`, `total_children`, `relevant_children`, then `PARENT_COLUMNS`. The counts are
  the proxy's, unchanged (D13).
- US1's detail route returns the same record. US2 adds `children` to it, ahead of the published
  columns: the parent's determinations, in the determination list shape, taken from the
  determination queryset passed through the visibility filter for the requester, so the attached
  list is exactly what the determination route would serve them (D16, research R13).
- Queryset: `GHFDBParent.objects.as_ghfdb_flat().with_child_counts()` with the exploration-purpose
  prefetch, ordered by `ghfdb_id, pk`.

### Determinations (US2)

- List record keys: `url`, `parent` (a link to the parent's detail route), `lat_NS`, `long_EW`, then
  `CHILD_COLUMNS`, then `ID` (D15).
- Detail record: the same keys, with `parent` as the parent's full record (the US1 parent record
  shape, without its attached determinations, so the nesting stops at one level).
- Queryset: `GHFDBChild.objects.for_export()`, narrowed to determinations whose parent is in the
  parent route's queryset after the visibility filter for the requester, as a subquery (D16,
  research R13). Every served determination therefore has a served parent, so `parent` is never
  `null`. Ordered by `ghfdb_id, pk`. The detail route loads the parent through the parent queryset
  of US1 in one further query.

### Released row (US3)

- Row keys: `PARENT_COLUMNS`, then `CHILD_COLUMNS`, then `ID`, which is `GHFDB_COLUMN_ORDER` with
  the meta columns the portal does not hold left out (D15). Nothing else. No `url` (FR-010,
  research R12).
- `explo_purpose` overridden to `sample.heatflowinterval.site.explo_purpose`.
- `as_ghfdb_flat()` on the child queryset gains `quality_parent` from `parent__quality`.
- Queryset: the determination route's queryset (the same narrowing by served parent). Detail
  addressed by the determination's `ghfdb_id`.

### Viewsets and registration

In `project/ghfdb/viewsets.py`, three `ReadOnlyModelViewSet` subclasses sharing one small base:

- `lookup_field = "ghfdb_id"`, `lookup_value_regex = "[0-9]+"`.
- `filter_backends = [FairDMVisibilityFilter]` (research R4).
- Permission, pagination and throttling inherited from the framework's settings.
- DRF's own `get_object()`, not overridden, so the visibility filter and the object permission
  check run on the single-record route (D12).
- Hyperlinked fields name their view with the `api:` namespace (`api:ghfdb-parents-detail`).
- `extend_schema_view` gives each action a summary and the `ghfdb` tag. The determination detail
  action declares its own response serializer so the schema carries both shapes.

`project/ghfdb/urls.py` registers them on `fairdm_api_router` as `ghfdb/parents`, `ghfdb/children`
and `ghfdb/flat` with basenames `ghfdb-parents`, `ghfdb-children` and `ghfdb-flat` (research R1).

### Documentation

`docs/guides/published-structure-api.md`, linked from the docs index: what each endpoint is for, how
paging works, the anonymous request limit and what it means for reading the whole database, and one
worked request and response per endpoint (FR-019). Each story writes its own endpoint's section.

## Project Structure

```text
project/ghfdb/
├── managers.py          # quality_parent on the child queryset
├── serializers.py       # field classes, published_fields(), the record serializers
├── viewsets.py          # new: the three viewsets
└── urls.py              # router registration

tests/test_ghfdb/
├── test_managers.py     # extended
├── test_serializers.py  # new
├── test_viewsets.py     # new: HTTP behaviour, query counts, visibility, refusal of writes
└── test_urls.py         # new: registration, API index, schema

docs/guides/published-structure-api.md  # new
```

## Risks

- **The visibility filter's signed-in branch** ORs two querysets and applies `distinct()`. Combining
  annotated, aggregated querysets is where Django refuses most often. Each story tests a signed-in
  request, not only an anonymous one.
- **Polymorphic querysets** can issue one query per concrete type. The proxies return one type
  each, so the query-count tests will show it if that changes.
