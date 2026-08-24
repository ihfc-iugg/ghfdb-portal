# Reading the published structure

The portal stores heat flow as a normalised relational graph:

- a site
- the depth intervals within it
- the gradient and conductivity measured over each interval
- the heat flow determined from that pair
- the representative value for the site as a whole

The database the commission publishes is a flat file, one row per determination, with the site's
own values restated on every row that mentions it.

This page covers the reading direction between the two. For the fields themselves, see
[GHFDB Fields](../ghfdb_fields.md). For the entities and their relationships, see the
[conceptual model](ghfdb-conceptual-model.md).

## Two proxies

Two Django proxy models present the stored graph in the published shape without duplicating it.
Neither adds a table, a column or a migration that touches data.

| Proxy | Stands in for | Presents |
|---|---|---|
| `GHFDBChild` | `HeatFlow` | one row per determination, in the published child columns |
| `GHFDBParent` | `ParentHeatFlow` | one row per site, in the published parent columns |

### Only published records are visible

Membership of the published database is expressed by the published identifier being set, and by
nothing else. Both managers restrict every queryset they produce to records whose `ghfdb_id` is
not null, so a record that has never been published cannot be reached through either proxy by any
route, including the administrative changelists.

Reach the unpublished records through the underlying model instead:

```python
from heat_flow.models import HeatFlow
from ghfdb.models import GHFDBChild

GHFDBChild.objects.count()   # published determinations only
HeatFlow.objects.count()     # every determination the portal holds
```

The restriction survives filtering, ordering, counting, slicing and chaining.

## The query surface

Five methods, available on both the queryset and its manager.

### `GHFDBChild.objects.as_ghfdb_flat()`

Annotates every scalar published child column onto each row. The values come from:

- the site
- the interval
- the gradient
- the conductivity
- the probe metadata
- the site's representative value
- the corrections

Each annotation carries its published name.

```python
row = GHFDBChild.objects.as_ghfdb_flat().first()
row.lat_NS, row.T_grad_mean, row.corr_TOPO_flag
```

A relationship that is absent yields empty columns rather than a missing row or an error, and this
holds for each correction type independently.

### `GHFDBChild.objects.for_export()`

Calls `as_ghfdb_flat()` and attaches the many-valued columns:

- calculation method
- exploration purpose
- the gradient's methods and corrections
- the conductivity's descriptive vocabularies
- lithology
- stratigraphy
- probe type

Fifteen published child columns are many-to-many relationships and cannot be annotated, so a
complete published row is only available after this method, not after `as_ghfdb_flat()` alone.

### `GHFDBParent.objects.as_ghfdb_flat()`

The same for the published parent columns. `explo_purpose` is excluded because it is many-valued:
annotating a many-to-many field joins the through table and returns one row per site-and-purpose
pair. It is attached by `with_children()` instead.

### `GHFDBParent.objects.with_child_counts()`

Annotates each site with `total_children`, the number of determinations it holds, and
`relevant_children`, the number that contributed to its representative value. A site holding no
determinations counts zero rather than null.

### `GHFDBParent.objects.with_children()`

Attaches each site's determinations, and its exploration purposes, so reading them costs no query
per site.

### Query cost

No method above issues a number of queries that grows with the number of rows returned. That is a
tested guarantee rather than an intention: each one is measured at two different row counts and the
counts are compared to each other, so a plan that became linear would fail even if its absolute
count stayed under any particular bound.

## Column names come from one place

`ghfdb/constants.py` holds the canonical published column definitions — `PARENT_COLUMNS`,
`CHILD_COLUMNS` and the order they combine in. It is the single authority for what a published
column is called and where it sits.

Two names differ from the file the commission distributes. The portal uses `tc_pT_function` and
`Ref_IGSN`, and rejects a file whose header carries the misspelled `tc_pT_fuction` or `Ref_ISGN` as
an outdated template. The reasoning is in
[ADR 0003](../adr/0003-misspelled-published-columns-are-corrected-and-rejected.md). The wider rule
that published names are preserved exactly, casing included, is
[ADR 0002](../adr/0002-published-column-names-are-preserved-exactly.md).

Three published columns are present and always empty. `Ref_IGSN` has no field behind it by
decision. The portal holds no sample numbers, and identifiers belong on the framework's sample
model rather than in a dedicated heat flow field. `publication_reference` and `data_reference` wait
on the work that attaches literature to each record.

## The administrative changelists

Both proxies are registered as read-only changelists: no add, no change, no delete, and no link
from a row into an editable form. They are how the data assessment team reads the database, and
they are built for people who know the published file. The columns carry the published names and
appear in the published order, so a record can be found and read without translating between two
sets of names.

Neither changelist writes out a column list. Both ask `ghfdb/columns.py` for the display callables
belonging to a canonical list, in that list's order. A column added to the canonical definitions and
not to that mapping is refused by name when the application starts, rather than rendering blank.

Search covers the site name and the published site identifier. Filters cover:

- environment
- the heat production correction flag
- exploration method
- exploration purpose
- country
- region
- continent
- geological domain

The three backed by controlled vocabularies offer only the terms of their own vocabulary, shown as
labels and not as stored keys.

### Importing

Both changelists carry an import action, and only the determination changelist carries an export.
Import requires the model's add permission. View permission alone is not enough, because import
writes. The resources themselves are documented with the
[import and export pipeline](../guides/importing-data.md).
