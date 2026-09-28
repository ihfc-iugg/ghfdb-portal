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

## D2 — A determination carries its coordinates, and no other parent column

Coordinates are the one parent value a determination cannot be used without: an unplaced
determination can be neither plotted nor joined to anything else. Every other parent column is one
request away through the parent link, and on the determination's own route it is already present in
full.

This is a deliberate exception to "a child record carries child columns", taken because the
alternative — a consumer issuing one request per determination to discover where it was made —
is the expensive shape for the commonest use.

## D3 — The parent link is a link in a list and a record on a single determination

A list route serves many records and is the common request; a single-record route serves one and is
the rarer one. Nesting the parent whole in both would make every page carry a complete parent per
row, most of them repeated. Nesting it in neither would make reading one determination a two-request
job for information the portal already has in hand.

The cost is that the schema describes two shapes for a determination. That is ordinary for a
generated API and is visible in the documentation the framework produces.

## D4 — Many-valued columns are lists, not the published file's joined cell

The published file joins several values into one cell with a separator, because a spreadsheet cell
holds one string. The API is not a spreadsheet, and a consumer given the joined string cannot split
it reliably — some vocabulary labels contain a comma already.

A consumer who wants the file's cell joins the list. A consumer who is given the string and needs
the values cannot get back to them. The lossless direction is the one to serve.

## D5 — Records are addressed by their published identifier

The framework addresses its own records by their internal identifier. These endpoints address
records by the identifier the published file carries, so that a consumer holding a row from a
release can go straight to its record without a lookup. The portal's own identifiers do not appear
in any of the three responses.

## D6 — The two determination counts stay on the parent list route

They are not published columns, and the flat endpoint therefore excludes them. On the parent
endpoint they earn their place: the proxy already computes both in the page query, so they cost no
additional query, and they are what tells a consumer whether a representative value rests on one
determination or on several.

The risk is the query plan at full size — the portal holds a sample rather than the database, so
the aggregate has not been measured against a realistic row count. Measuring it is a planning task.
If it proves expensive, the counts move onto the record rather than out of the response.

## D7 — An absent value is empty, never a missing key

A consumer parsing a page needs the same column set on every record; a key that appears only when
it has a value forces defensive handling of every column. A column with no value is emitted empty,
and a many-valued column with no related records is an empty list — which is distinguishable from a
scalar with no value, and deliberately so.

## D8 — The flat endpoint is named for the shape it serves

The alternatives were the published product's own words. "Release" was rejected because the portal
will later generate and serve actual releases as citable artefacts (R11), and two different things
under one name is exactly the naming failure CONTEXT.md exists to prevent. "Spreadsheet" was
rejected because CONTEXT.md names three spreadsheets and the word alone does not say which. "Flat"
names the shape — one row, no nesting — and claims nothing it is not.

## D9 — The release format, not the upload template

Exports are always written in the release format, and it is the format a consumer of the published
product recognises. The upload template is a contributor's input.

The release format carries columns the portal does not hold: the review status, the year, and a
supplied quality code the portal refuses on principle because it computes its own. Those are
assembled into a release file alongside the portal's data, which is R17's work. This endpoint serves
what the portal holds, in the released row's shape and order.

## D10 — What is deliberately not in this feature

- **A comma-separated download of the whole database.** The flat endpoint is where a second
  representation would attach, and R8 owns replacing the static download with the portal's own data.
- **Filtering and searching beyond the framework's defaults.** Worth having and worth specifying
  properly; not worth quietly attaching to this feature.
- **The existing static download of the 2024 release and the column-metadata route beside it.**
  Both stay. Retiring the static download belongs to R8, which is what replaces it.
- **Anything that writes.** The routes into the portal are the import paths.

## D11 — The framework's visibility filter stays, ordering and field filtering do not

Decided at planning. The proxies decide which records belong to the published database. The
framework's visibility filter decides whether a record's dataset may be shown to the person asking.
Keeping it means a record carrying a published identifier in a private dataset is never served to an
anonymous consumer. The framework's ordering backend would offer ordering on the many-valued
columns, which repeats a record once per related value, so it is dropped with the field-filter
backend. Pages are ordered by published identifier.

## D12 — A duplicated published identifier resolves to the earliest record

Decided at planning. The database does not make a published identifier unique, though both import
paths upsert on it. A single-record route matching two records answers with the one created first
rather than a server error. List routes carry both records as they are.

## D13 — The child counts count published determinations

Decided at planning. A determination with no published identifier is outside the published
database and unreachable through these endpoints, so a parent counting it would report more
determinations than its attached list holds. Both counts narrow to determinations carrying a
published identifier, in the proxy, so the admin's parent list agrees with its own child list too.

## D14 — An empty scalar is `null`

Decided at planning. D7 settles that an absent value is present and empty. For a scalar, empty is
`null`, and an empty string is emitted as `null` too: the two columns nothing resolves are annotated
as empty strings, and a consumer gains nothing from telling the two apart.

## D15 — The released row carries no identifier of its own

Decided at planning, as a reading of the spec rather than a change to it. The spec defines the flat
row as the published parent columns followed by the published child columns, in the order the
constants module holds, and SC-006 admits no other key. The determination's own identifier is held
there as a meta column, outside both lists, so the row carries `ID_parent` but not `ID`. A consumer
still reaches a single row by `ID`, which addresses the route.

## Open, and carried rather than resolved

**The canonical column vocabulary is disputed in one place** ([#122](https://github.com/ihfc-iugg/ghfdb-portal/issues/122)):
six columns have no agreed metadata, and one site column's annotation key disagrees with its test.
This feature reads the canonical column list rather than restating it, so it inherits whatever that
dispute settles on. It does not settle it, and it must not publish a column name that #122 later
changes — the planning stage checks which of the disputed names this feature's responses would
expose, and that check gates the story that exposes them.
