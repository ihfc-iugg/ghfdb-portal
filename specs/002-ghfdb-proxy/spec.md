# Feature Specification: The published structure read from the model

**Feature Branch**: `002-ghfdb-proxy`

**Created**: 2026-04-10

**Rewritten**: 2026-08-23 — audited against the implementation and rewritten in place. The
adjudications behind every change are recorded in [decisions.md](decisions.md).

**Status**: Draft

**Goals**: G2 — faithful two-way translation between the relational model and the published
structure, so internal queries stay predictable and exports match the published format exactly

**Roadmap**: R2

**References**: Fuchs et al. (2021); Fuchs et al. (2023); constitution principles II, III, IX;
ADR-0001, ADR-0002, ADR-0003, ADR-0007

## Overview

The portal stores heat flow as a normalised relational graph:

- a site
- the depth intervals within it
- the gradient and conductivity measured over each interval
- the heat flow determined from that pair
- the representative value for the site as a whole

The database the commission publishes is a flat file, one row per determination, with the site's
own values restated on every row that mentions it.

This feature is the reading direction between the two. It presents the stored graph in the
published shape without duplicating it, through two proxy models that add no table and no column:
`GHFDBChild` over `HeatFlow`, and `GHFDBParent` over `ParentHeatFlow`. Each carries a queryset that
flattens the relationships it needs into published columns, in a number of queries that does not
grow with the number of rows. Each is also scoped so that only records belonging to the published
database are visible at all.

Both are registered as read-only admin changelists. Those changelists are how the assessment team
reads the database, and they are built for people who know the published file. The columns carry
the published names and appear in the published order, so a curator can find a record and read it
without translating between two sets of column names. Search and filters scoped to their
vocabularies make that workable across the whole database, not just the page on screen.

The proxies are also the surface the import and export resources attach to. Those resources, and
the writing direction generally, are specified in `003-ghfdb-import-export`. What belongs here is
the query surface they consume and the admin they hang off.

The canonical column definitions live in the extraction app's constants module, which names the
published columns exactly as the published file names them (ADR-0002), with two corrections
(ADR-0003). This feature treats that module as the single authority for what the columns are called
and what order they come in. Nothing in this feature restates a column list that the module already
holds.

## User Scenarios & Testing

### User Story 1 — Determinations read in the published shape (Priority: P1)

A developer or a curator asks for heat flow determinations in the shape the published file has —
one row per determination, carrying the site metadata, the interval geometry, the gradient, the
conductivity and the corrections that belong to it — and gets them without writing the joins by
hand and without the query cost growing with the number of rows.

**Why this priority**: everything downstream of the stored model reads through this. The export,
the admin, and eventually the API all consume the same flattened rows, and each one that assembles
them independently is another place the published structure can be got wrong.

**Independent Test**: build several complete record chains, ask the queryset for all of them, and
assert both that every published child column resolves on every row and that the number of queries
does not change when rows are added.

**Acceptance Scenarios**:

1. **Given** a database holding complete record chains — site, interval, gradient, conductivity,
   determination, corrections and the site's representative value — **When** the child queryset is
   asked to flatten them, **Then** every published child column resolves on every row.
2. **Given** the same request, **When** the number of stored chains is increased, **Then** the
   number of database queries is unchanged.
3. **Given** a determination whose gradient, conductivity, probe metadata or a particular
   correction is absent, **When** the rows are flattened, **Then** the row is returned with those
   columns empty rather than being dropped or raising.
4. **Given** the proxy, **When** ordinary queryset operations are used — filtering, ordering,
   counting, slicing — **Then** they behave as they do on the model the proxy stands in for.
5. **Given** a determination whose published identifier is not set, **When** any query is made
   through the proxy, **Then** that record is not among the results.

---

### User Story 2 — Sites read in the published shape, with their determination counts (Priority: P1)

A curator or a developer asks for sites in the published parent shape — one row per site with the
representative value, the site metadata and the geography — and needs to know, per site, how many
determinations it holds and how many of them contributed to the representative value.

**Why this priority**: the two counts are the assessment team's fastest read on whether a site's
representative value rests on the evidence they expect. They are also what makes the site-level
changelist worth having rather than a duplicate of the determination-level one.

**Independent Test**: build sites with differing numbers of contributing and non-contributing
determinations, ask for the counts, and assert both correctness and a query count that does not
grow with the number of sites.

**Acceptance Scenarios**:

1. **Given** sites holding determinations of which only some contributed to the representative
   value, **When** the site queryset is asked for its counts, **Then** each row carries the total
   number of determinations and the number that contributed.
2. **Given** the same request, **When** the number of stored sites is increased, **Then** the
   number of database queries is unchanged.
3. **Given** a site holding no determinations, **When** the counts are read, **Then** both are zero
   rather than empty.
4. **Given** the site queryset, **When** it is asked to flatten to the published parent columns,
   **Then** every published parent column resolves on every row.
5. **Given** the site queryset, **When** it is asked to attach the determinations belonging to each
   site, **Then** reading them adds no query per site.
6. **Given** a site whose published identifier is not set, **When** any query is made through the
   proxy, **Then** that site is not among the results.

---

### User Story 3 — The assessment team reads the database in the terms they know (Priority: P2)

A member of the assessment team opens the portal's administrative interface to check a record. They
know the published file's column names and the order they come in, and they should not have to
learn a second set of names to read the same data here.

**Why this priority**: it is what makes the stored model usable by the people who maintain the
database, and a changelist in an unfamiliar order costs their time on every visit rather than once.

**Independent Test**: open both changelists as a staff user against stored records, and assert the
columns, their order, their headings, the search behaviour and the filter choices.

**Acceptance Scenarios**:

1. **Given** stored determinations, **When** a staff user opens the determination changelist,
   **Then** it renders, and the published child columns appear in the published order under the
   published headings.
2. **Given** the determination changelist, **When** the user reads its leading columns, **Then**
   they carry enough of the site to identify which record a row belongs to, without restating the
   site's own values on every row.
3. **Given** stored sites, **When** a staff user opens the site changelist, **Then** it renders, and
   the published parent columns appear in the published order under the published headings,
   followed by the geography and the two determination counts.
4. **Given** either changelist, **When** the user searches by site name or by published site
   identifier, **Then** matching rows are returned.
5. **Given** either changelist, **When** the user opens a filter backed by a controlled vocabulary
   — environment, exploration method, exploration purpose — **Then** the choices offered are the
   terms of that vocabulary and no others, shown as their labels rather than their stored keys.
6. **Given** either changelist, **When** the user filters by country, region, continent or
   geological domain, **Then** matching rows are returned.
7. **Given** either changelist, **When** the user attempts to add, change or delete a record,
   **Then** the interface offers no route to do so.
8. **Given** either changelist, **When** the number of stored records is increased, **Then** the
   number of queries the page issues is unchanged.

---

### Edge Cases

- A determination whose interval, site, gradient, conductivity or probe metadata is absent: every
  column sourced from the missing relationship is empty and the row is still returned.
- A correction type never recorded against a determination: that correction's column is empty.
- A site holding no determinations: both counts read zero.
- A record whose published identifier is not set: invisible through either proxy, on every path,
  including the changelists.
- `Ref_IGSN`: present as a column and always empty. The portal holds no sample numbers, by decision
  (ADR-0003 covers the spelling, and the absence of the field is recorded in `decisions.md`).

## Requirements

### Functional Requirements

**The proxies**

- **FR-001**: The system MUST provide a `GHFDBChild` proxy over `HeatFlow` and a `GHFDBParent`
  proxy over `ParentHeatFlow`. Neither may add a database table, a column or a migration that
  touches data.
- **FR-002**: Membership of the published database MUST be expressed by the published identifier
  being set, and by nothing else. Both proxies MUST restrict every queryset they produce to records
  whose published identifier is set, so that a record which has never been published cannot be
  reached through either proxy by any route.
- **FR-003**: Both proxies MUST behave as the models they stand in for under ordinary queryset
  operations — filtering, ordering, counting, slicing and chaining — with the restriction in FR-002
  surviving each of them.

**Flattening**

- **FR-004**: The child queryset MUST expose a method that annotates every published child column
  onto each row, sourced from the site, the interval, the gradient, the conductivity, the probe
  metadata, the site's representative value and the corrections.
- **FR-005**: The number of queries issued by FR-004 MUST NOT grow with the number of rows
  returned.
- **FR-006**: A relationship that is absent MUST yield empty columns rather than a missing row or
  an error. This applies to each correction type independently.
- **FR-007**: The child queryset MUST expose a second method that adds the many-valued
  relationships needed to write a row out — calculation method, exploration purpose, the gradient's
  methods and corrections, the conductivity's descriptive vocabularies, lithology, stratigraphy and
  probe type. Its query count MUST NOT grow with the number of rows returned either.
- **FR-008**: The parent queryset MUST expose a method annotating every published parent column
  onto each row.
- **FR-009**: The parent queryset MUST expose a method annotating each site with the number of
  determinations it holds and the number that contributed to its representative value, in a query
  count that does not grow with the number of sites.
- **FR-010**: The parent queryset MUST expose a method attaching each site's determinations such
  that reading them costs no query per site.
- **FR-011**: Where an annotation's published name collides with a field the framework's base class
  already declares, the annotation MUST carry a distinct name and the published name MUST be
  restored at the surface that presents it. No other annotation may deviate from its published name
  (ADR-0002).

**The changelists**

- **FR-012**: Both proxies MUST be registered with the administrative interface as read-only:
  no add, no change, no delete, and no link from a row into an editable form.
- **FR-013**: The determination changelist MUST show the published child columns, in the order the
  canonical column definitions give them, under the published headings. That order MUST be derived
  from the canonical definitions rather than restated, so that the two cannot disagree.
- **FR-014**: The determination changelist MUST precede those columns with the record's published
  identifier, the site's published identifier, the site name and the site's coordinates, and with
  nothing else. Site values that do not vary between a site's determinations MUST NOT be repeated
  on every row.
- **FR-015**: The site changelist MUST show the published parent columns, in the order the
  canonical column definitions give them, under the published headings, derived from those
  definitions rather than restated. It MUST then show country, region, continent and geological
  domain, and then the two determination counts.
- **FR-016**: Both changelists MUST support text search on the site name and on the published site
  identifier.
- **FR-017**: Both changelists MUST offer filters on environment, heat production correction flag,
  exploration method, exploration purpose, country, region, continent and geological domain.
- **FR-018**: Every filter backed by a controlled vocabulary MUST offer only the terms of that
  vocabulary, and MUST show each term's label rather than its stored key. This applies to
  environment, exploration method and exploration purpose, on both changelists.
- **FR-019**: The number of queries either changelist issues MUST NOT grow with the number of rows
  it displays.
- **FR-020**: Neither changelist may traverse a relationship path that does not exist on the model
  it queries.

**Resource attachment**

- **FR-021**: The determination changelist MUST carry the determination import resource and the
  export resource. The site changelist MUST carry the site import resource and no export resource.
  No resource may be attached to both. The resources themselves belong to
  `003-ghfdb-import-export`. What this feature owns is where they attach.

## Success Criteria

- **SC-001**: Every published child column resolves on every row of the flattened child queryset,
  proven by a test that reads the column list from the canonical definitions rather than from a
  copy.
- **SC-002**: Every published parent column resolves on every row of the flattened parent queryset,
  proven the same way.
- **SC-003**: Adding rows does not add queries. Proven for the child flattening, the child export
  queryset, the parent counts, the parent flattening, the parent attachment of determinations, and
  both changelists, each measured at two different row counts rather than one.
- **SC-004**: The determination counts are correct for sites holding some contributing
  determinations, all contributing, none contributing, and none at all.
- **SC-005**: A record whose published identifier is not set is unreachable through either proxy,
  proven on the manager, on a chained queryset, and on both changelists.
- **SC-006**: A row whose gradient, conductivity, probe metadata or a given correction is absent is
  returned with those columns empty, proven for each correction type independently.
- **SC-007**: Both changelists render for a staff user, and the columns they render, in order and
  by heading, match the canonical column definitions — proven by a test that fails when the
  canonical definitions change and the changelist does not.
- **SC-008**: Neither changelist offers a route to add, change or delete.
- **SC-009**: Each vocabulary-backed filter offers exactly the terms of its vocabulary, proven on
  both changelists, and offers no term belonging to another vocabulary.
- **SC-010**: The resources attached to each changelist are exactly those FR-021 names, proven for
  both import and export on both changelists.
- **SC-011**: No test in this feature's suite is expected to fail.

## Out of Scope

- The writing direction. Import and export resources, format detection, vocabulary normalisation
  and round-trip fidelity all belong to `003-ghfdb-import-export`. This feature defines only the
  query surface and the attachment points those resources use.
- The relational model itself. Fields, relationships and constraints belong to
  `001-heat-flow-data-model`.
- The map viewer page and its menu entry. It shares this application and nothing else, and the
  roadmap item that replaces the embedded viewer with one running inside the portal owns it from
  here.
- The column metadata file and the routes that serve it. Whether that file should exist at all is
  an open question belonging to the roadmap item covering the API.
- A field holding sample numbers. The reasons are recorded in `decisions.md`. The published column
  stays, and it stays empty.
- Release records and release generation (ADR-0007).
- Quality score calculation. Both proxies present the stored code and neither computes it.

## Assumptions

- The canonical column definitions in the extraction app's constants module are the authority for
  what the published columns are called and what order they come in. Every column list in this
  feature derives from that module.
- The relational model, its polymorphic base classes and its multi-table inheritance are as
  `001-heat-flow-data-model` specifies. Reaching an interval's own fields from a determination
  goes through the inheritance accessor.
- A proxy model adds no table, so the only migrations this feature can require are the ones that
  record a proxy's existence and its permissions.
- Controlled vocabularies are declared in the heat flow application's vocabulary module and are
  the source for every filter this feature scopes.
- The portal runs SQLite in development and PostgreSQL in production, so no behaviour here may
  depend on a capability only one of them has.

## Clarifications

### Session 2026-08-23

- Q: Is the exact left-to-right column order of the changelists a requirement, or was it a
  stand-in for "the flat structure is correct" that the export resource now owns? → A: A
  requirement. The changelists are how data administrators view the database, and they know it as
  the published spreadsheet. A different column order would draw complaints and questions from
  users who know only that file.
- Q: The published file leads each row with the full parent block. The determination changelist
  instead shows four site columns for orientation and then the child block. Which is intended? →
  A: The four-column prefix. Site values that do not vary across a site's determinations are noise
  when repeated per row. The familiarity being protected is the child block's.
- Q: The changelists carry `tc_pT_fuction`, `Ref_ISGN` and `quality`, while the canonical
  definitions carry `tc_pT_function`, `Ref_IGSN`, `quality_child` and `quality_parent`. Which
  wins? → A: The canonical definitions. ADR-0003 already rules that the portal uses the corrected
  spellings internally and rejects the misspelled forms on input, and the assessment team reading
  these changelists are the people who can get the published template corrected. The tail of the
  child block reorders to match, and the quality columns take their canonical names.
- Q: `Ref_IGSN` renders empty on every row because the field that held sample numbers was deleted.
  Does the column stay? → A: Yes, empty. The published structure defines it, and a missing column
  confuses a curator comparing against the file more than a blank one does. Whether the portal
  should hold sample numbers at all is settled separately and negatively — see `decisions.md`.
- Q: Does the map viewer page belong to this feature? → A: No. Remove it.
- Q: Does this feature bring the column metadata file onto the canonical column names? → A: No.
  That file and the routes that serve it are an open question for the API work, and this feature
  leaves both alone.
