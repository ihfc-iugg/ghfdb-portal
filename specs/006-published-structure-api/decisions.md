# Decisions — 006 published structure API

Decisions taken during this feature, and why. Fine-grained rationale that would clutter
[spec.md](spec.md) lives here; the gate-level trail lives on the feature's issue.

## D1 — Three endpoints, not one

**Settled at intake.** The first reading of this feature had two endpoints, parents and children,
with a child record carrying its parent's columns repeated so that a page of children was a page of
released rows. That conflates two things: a determination, and the released row a determination
appears in. A determination's own record should describe the determination.

The released row is still worth serving exactly as published — it is what a consumer of the
published file recognises, and it is the shape an export writes — so it became an endpoint of its
own rather than a property of the child endpoint.

**ADR:** none — shapes this feature's endpoints only; the spec records it.

## D2 — A determination carries its coordinates, and no other parent column

Coordinates are the one parent value a determination cannot be used without: an unplaced
determination can be neither plotted nor joined to anything else. Every other parent column is one
request away through the parent link, and on the determination's own route it is already present in
full.

This is a deliberate exception to "a child record carries child columns", taken because the
alternative — a consumer issuing one request per determination to discover where it was made —
is the expensive shape for the commonest use.

**ADR:** none — a field choice local to the determination record.

## D3 — The parent link is a link in a list and a record on a single determination

A list route serves many records and is the common request; a single-record route serves one and is
the rarer one. Nesting the parent whole in both would make every page carry a complete parent per
row, most of them repeated. Nesting it in neither would make reading one determination a two-request
job for information the portal already has in hand.

The cost is that the schema describes two shapes for a determination. That is ordinary for a
generated API and is visible in the documentation the framework produces.

**ADR:** none — a response-shape choice local to the determination endpoint.

## D4 — Many-valued columns are lists, not the published file's joined cell

The published file joins several values into one cell with a separator, because a spreadsheet cell
holds one string. The API is not a spreadsheet, and a consumer given the joined string cannot split
it reliably — some vocabulary labels contain a comma already.

A consumer who wants the file's cell joins the list. A consumer who is given the string and needs
the values cannot get back to them. The lossless direction is the one to serve.

**ADR:** none — a serialisation choice local to these endpoints, recorded in the spec.

## D5 — Records are addressed by their published identifier

The framework addresses its own records by their internal identifier. These endpoints address
records by the identifier the published file carries, so that a consumer holding a row from a
release can go straight to its record without a lookup. The portal's own identifiers do not appear
in any of the three responses.

**ADR:** none — the addressing is stated in the spec and visible in every route; nothing beyond these endpoints inherits it.

## D6 — The two determination counts stay on the parent list route

They are not published columns, and the flat endpoint therefore excludes them. On the parent
endpoint they earn their place: the proxy already computes both in the page query, so they cost no
additional query, and they are what tells a consumer whether a representative value rests on one
determination or on several.

The risk is the query plan at full size — the portal holds a sample rather than the database, so
the aggregate has not been measured against a realistic row count. Measuring it is a planning task.
If it proves expensive, the counts move onto the record rather than out of the response.

**ADR:** none — local to the parent endpoint.

## D7 — An absent value is empty, never a missing key

A consumer parsing a page needs the same column set on every record; a key that appears only when
it has a value forces defensive handling of every column. A column with no value is emitted empty,
and a many-valued column with no related records is an empty list — which is distinguishable from a
scalar with no value, and deliberately so.

**ADR:** none — a serialisation choice local to these endpoints, recorded in the spec.

## D8 — The flat endpoint is named for the shape it serves

The alternatives were the published product's own words. "Release" was rejected because the portal
will later generate and serve actual releases as citable artefacts (R11), and two different things
under one name is exactly the naming failure CONTEXT.md exists to prevent. "Spreadsheet" was
rejected because CONTEXT.md names three spreadsheets and the word alone does not say which. "Flat"
names the shape — one row, no nesting — and claims nothing it is not.

**ADR:** none — a naming choice, recorded here and in the guide.

## D9 — The release format, not the upload template

Exports are always written in the release format, and it is the format a consumer of the published
product recognises. The upload template is a contributor's input.

The release format carries columns the portal does not hold: the review status, the year, and a
supplied quality code the portal refuses on principle because it computes its own. Those are
assembled into a release file alongside the portal's data, which is R17's work. This endpoint serves
what the portal holds, in the released row's shape and order.

**ADR:** none — the spec's clarification records it.

## D10 — What is deliberately not in this feature

- **A comma-separated download of the whole database.** The flat endpoint is where a second
  representation would attach, and R8 owns replacing the static download with the portal's own data.
- **Filtering and searching beyond the framework's defaults.** Worth having and worth specifying
  properly; not worth quietly attaching to this feature.
- **The existing static download of the 2024 release and the column-metadata route beside it.**
  Both stay. Retiring the static download belongs to R8, which is what replaces it.
- **Anything that writes.** The routes into the portal are the import paths.

**ADR:** none — a scope boundary, not a design decision.

## D11 — The framework's visibility filter stays, ordering and field filtering do not

Decided at planning. The proxies decide which records belong to the published database. The
framework's visibility filter decides whether a record's dataset may be shown to the person asking.
Keeping it means a record carrying a published identifier in a private dataset is never served to an
anonymous consumer. The framework's ordering backend would offer ordering on the many-valued
columns, which repeats a record once per related value, so it is dropped with the field-filter
backend. Pages are ordered by published identifier.

**ADR:** none — local to these viewsets; ADR 0021 carries the part that generalises.

## D12 — A single record is found by the framework's own lookup

Decided at planning. The published identifier is not unique in the database, but both import paths
upsert on it, so no import can create a second record under an identifier. The viewsets keep DRF's
own `get_object()`, which is also where the visibility filter and the object permission check run
on a single-record route. Overriding it to guard a state nothing produces would put both checks at
risk.

**ADR:** none — keeps the framework's default; nothing new to record.

## D13 — The child counts are the proxy's

Decided at planning, after the design review. The counts are what the proxy computes, as the spec
was approved on (D6): every determination at the site, and every one of those that contributed.
That includes a determination not yet carrying a published identifier, which a curator sees
arriving in the admin, and one in a dataset not yet approved, so the counts reveal that such a
determination exists. The consumer guide says so, because a parent's counts can then exceed the
determinations its own route lists.

**ADR:** none — leaves existing behaviour unchanged.

## D14 — An empty scalar is `null`

Decided at planning. D7 settles that an absent value is present and empty. For a scalar, empty is
`null`, and an empty string is emitted as `null` too: the two columns nothing resolves are annotated
as empty strings, and a consumer gains nothing from telling the two apart.

**ADR:** none — a serialisation choice local to these endpoints.

## D15 — A determination's own identifier is carried as `ID`

Decided at planning, after the design review. The flat endpoint mirrors the release format
(clarification Q1). Clarification Q2 names the release columns the endpoint does not carry: the
review status, the year and the quality code. The determination's own identifier is none of those.
Clarification Q3 calls it the identifier a published file carries as the row's own. So it is
carried, as `ID`, where the canonical order in the constants module puts it: after the child
columns. The determination record carries it in the same place. Without it a consumer paging the
flat rows could not tell two determinations at one site apart, or reach a row's own route.

**ADR:** none — a reading of the spec's clarifications, local to two record shapes.

## D16 — A determination is served only through a parent that is served

Decided at planning, after the design review. Visibility is decided per record, and a determination
and its parent can sit in different datasets: an upload under review can name a public parent, and
a determination can attach by its coordinates to a site that is not yet public. Served naively,
the first leaks an unapproved determination through its public parent's route, and the second leaks
an unapproved parent's values through the determination's parent columns.

So the published structure is served whole or not at all. The determination and flat routes serve
a determination only when its parent is one the parent route would serve to the same requester. A
parent's attached determinations are the ones the determination route would serve to that
requester. A determination with no parent, or with a parent carrying no published identifier, is
outside the two-level structure and is not served.

**ADR:** docs/adr/0021-a-determination-is-served-only-through-a-served-parent.md

## D17 — The count aggregate is not measured at release size here

Decided at planning. D6 asks for the parent page's count aggregate to be measured against a
realistic row count. The portal holds a sample, and the development environment has no PostgreSQL,
so a measurement here would be of SQLite on a few hundred rows and would say nothing about
production. The query is one grouped join of parents to their determinations on an indexed foreign
key, which PostgreSQL answers with a single hash aggregate. D6's fallback stands if it proves
expensive once the database is loaded: the counts move onto the record, not out of the response.

**ADR:** none — a deferred measurement, not a design decision.

## D18 — `published_fields()` omits `source` when the accessor equals the column name

Decided during US1 implementation (T001). DRF's `Field.bind()` refuses a `source` argument equal to
the field name it is bound under, and most `PublishedColumns.ENTRIES` accessors equal the published
column name by design (the entry's `accessor` defaults to `None` for exactly that reason). Passing
`source=accessor` unconditionally would raise `AssertionError` for every one of those columns the
first time `published_fields()`'s output was bound into a real serializer. `published_fields()`
passes `source` only when the accessor differs from the column name, and lets `Field.bind()` default
the rest to the field name itself, which is the same value. **Revisit if**: DRF changes `bind()`'s
redundant-source check, or `PublishedColumns.ENTRIES` stops using `None` to mean "same as the name".

**ADR:** none — an implementation detail of one helper.

## D19 — The query-count test builds to a literal page of 100, not the fixture default

Decided during US1 implementation (T002). `tests/test_ghfdb/conftest.py`'s `constant_query_count`
defaults to `low=2, high=4`, which every other caller in this suite uses unchanged. SC-003 states the
comparison literally — "a page of one record and a page of the maximum size" — so
`test_query_count_is_constant_between_a_page_of_one_and_a_full_page` calls it with `low=1, high=99`
(cumulative 100) and a fixed `page_size=100`, so the final `call()` genuinely renders a full
100-record page rather than a handful of rows under a page size nothing constrains. **Revisit if**:
building 100 site+parent chains per test run becomes a measured cost problem — `low=2, high=4` still
proves query-count invariance, just not at SC-003's literal page size.

**ADR:** none — a test-construction choice.

## D20 — The consumer guide carries a short "Implementation notes" section

Decided during US1 implementation (T003). The documentation check failed: `PublishedValueField`, `ConceptLabelsField`, `published_fields`, `GHFDBBaseViewSet`,
`GHFDBParentSerializer` and `GHFDBParentViewSet` are new public names in `project/ghfdb/` that no
page under `docs/` quoted as code (`docs-undocumented`). T003's own description does not ask for
this — the guide is written for an HTTP consumer, who has no reason to know these Python names.
Rather than satisfy the check with a bare, out-of-context list, `published-structure-api.md` gained a
short "Implementation notes" section explaining the shared serializer builder and viewset base class
US2 and US3 reuse — genuinely useful to a contributor extending the API, not padding written to
quiet a linter. **Revisit if**: the guide grows large enough that internals belong on a separate
development-facing page instead.

**ADR:** none — a documentation choice local to one page.

## D21 — `parent` and `children` are built in `get_fields()`, never declared as class attributes

Decided during US2 implementation (T004, T005). `DRF`'s own `Field` base class carries a `parent`
attribute (the field's owning serializer, set by `bind()`), and every `Serializer` is itself a
`Field`. Declaring a class attribute named `parent` on `GHFDBChildListSerializer` shadowed that
attribute's type and failed the typecheck. Similarly, `ParentHeatFlow.children` is the model's own
reverse relation manager; a view cannot reassign it to a filtered queryset (`TypeError: Direct
assignment to the reverse side of a related set is prohibited`). Both fields are instead added in
`get_fields()`, alongside the ones `published_fields()` already builds that way, and `children`
reads a differently-named attribute (`children_list`) the view sets on the instance before
serializing. **Revisit if**: DRF or the model gains a field of either name for an unrelated reason,
since either add would collide with the same names again.

**ADR:** none — an implementation detail forced by DRF's own names.

## D22 — Orbit is switched off for the test suite

Decided during US2. The framework installs Orbit, which records every request by writing rows on
the same database connection. A test that counts the queries behind a page counted those rows
too, and how many there were depended on cache state, so the query-count tests failed
intermittently when files ran together. `tests/conftest.py` sets `ENABLED: False` in
`ORBIT_CONFIG` before Django is set up, which also skips installing Orbit's watchers.

**ADR:** none — test-suite configuration, applied under an existing project convention.

## D23 — A single record is checked against the measurement view permission

Decided at code review. The framework's object permission check asked for the proxy model's own
view permission, which guardian cannot check against an object whose concrete model lives in
another app. A signed-in user allowed to see a private record got a server error on its route. The
viewsets check `measurement.view_measurement` for a read, the same permission the list filter
already resolves to, so a record's list entry and its own route agree.

**ADR:** none — a correction local to these viewsets' permission class.

## D24 — A parent is served only where its site is visible too

Decided at code review. A parent's site columns are read from the site, which sits in a dataset of
its own and can be updated by an upload that is not yet approved. The parent route narrows to
parents whose site is visible to the requester, and the determination and flat routes inherit it
through D16.

**ADR:** docs/adr/0021-a-determination-is-served-only-through-a-served-parent.md

## Open, and carried rather than resolved

**The canonical column vocabulary is disputed in one place** ([#122](https://github.com/ihfc-iugg/ghfdb-portal/issues/122)):
six columns have no agreed metadata, and one site column's annotation key disagrees with its test.
This feature reads the canonical column list rather than restating it, so it inherits whatever that
dispute settles on. It does not settle it, and it must not publish a column name that #122 later
changes — the planning stage checks which of the disputed names this feature's responses would
expose, and that check gates the story that exposes them. Planning found that none of the
disputed items is a published column name (research R10), so no story was gated on it.
