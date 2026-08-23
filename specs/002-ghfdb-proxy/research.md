# Research — 002 the published structure read from the model

What had to be established before the open work could be planned. Every claim below was checked
against the code or verified at runtime, and cites where.

## R1 — How a changelist's columns can be derived from the canonical definitions

**Question**: FR-013 and FR-015 require the column order to come from `constants.py` rather than be
restated. Django's `list_display` is a tuple of names. What can go in it, and how does a published
column name reach the screen as a heading?

**Findings**

Django accepts four kinds of entry in `list_display`: a field on the model, a callable, the name of
a method on the admin class, or the name of a method on the model. Anything else fails the system
check `admin.E108` at startup, so a derived tuple is checked at import time rather than at request
time — a mismatch between the canonical definitions and what the admin can serve is a startup
failure, not a broken page.

Only the callable forms can carry an arbitrary heading. `short_description` on the callable sets
it. A bare model field takes its heading from the field's `verbose_name`, which is not the published
name for any column where the two differ.

The published columns fall into four groups, and the group decides the callable:

1. **Queryset annotations** — 34 of the child columns and 14 of the parent's. Read the attribute off
   the row. This is what the existing `_scalar()` factory does (`admin.py:104`).
2. **Fields on the proxy itself** — `ghfdb_id`, `expedition`, `c_comment`, `water_temperature`,
   `quality`. Three of these already carry the published name. `quality` does not: the published
   columns are `quality_child` and `quality_parent` (`constants.py:64,123`), so it needs a callable
   to set the heading even though the value is a plain attribute read.
3. **Many-valued relationships** — 17 child columns, 1 parent column. Join the related labels. The
   rows must be prefetched or this is the N+1 the feature exists to avoid.
4. **Columns nothing resolves** — see R4.

**Decision**: one mapping from published column name to its group and accessor, and a factory that
turns that mapping into the display callables and the `list_display` tuple, ordered by
`CHILD_COLUMNS` and `PARENT_COLUMNS`.

The mapping is the only place a published column appears in the admin. The order is not restated at
all — it is `constants.py`'s list order. A column added to the canonical definitions and missing
from the mapping fails at startup, which is the property FR-013 is asking for.

**Kept out of scope**: the import and export resources declare the same published names a third and
fourth time, as `column_name=` against snake_case attributes (`resources/child.py:120`,
`resources/export.py:100`). The same mapping would serve them and remove the duplication that
issue #122 is about. That is `003-ghfdb-import-export`'s work, and this feature does not touch those
files. The mapping is written so it can be adopted there without change.

## R2 — Proving that query cost does not grow with row count

**Question**: SC-003 requires every constancy claim to be measured at two row counts. The existing
tests measure one.

**Findings**

The existing assertions use `django_assert_max_num_queries` against the `heat_flow_chain` fixture,
which builds exactly one complete chain (`tests/test_ghfdb/conftest.py:36`). A bound satisfied at
one row is satisfied by a linear query plan as well as by a constant one, so the assertion cannot
fail for the reason it exists.

Two row counts and an equality between them is what distinguishes the two. `django_assert_num_queries`
gives the exact count, so the shape is: build *n* chains, count; build more, count again; assert the
two counts are equal. Comparing counts to each other rather than to a literal also survives a
framework change that adds or removes a fixed query, which a hard-coded bound does not.

**Cost**. The `ghfdb` suite takes 208 seconds for 154 tests, and the chain fixture dominates it —
it creates a site, an interval, probe metadata, a gradient, a conductivity, a parent, a child and
nine corrections, against a dataset factory. Repeating that per test at two row counts each is the
main risk to suite runtime in this work.

**Decision**: one session-independent fixture that builds a configurable number of chains, and one
that builds a small fixed number for the correctness tests. Constancy tests take the counted
fixture at two sizes; every other test takes the cheap one. Sizes stay small — the difference
between two and four rows proves the same thing as the difference between two and two hundred, and
costs two chains rather than a hundred and ninety-eight.

## R3 — What "every published column resolves" means for many-valued columns

**Question**: SC-001 requires every published child column to resolve on every row of the flattened
queryset. Seventeen of those columns are many-to-many relationships, which cannot be annotated.

**Findings**

FR-004 and FR-007 split the work deliberately: the first annotates the scalar columns, the second
attaches the many-valued ones. Only after both has a row got every published column on it. The
existing code has the same split — `as_ghfdb_flat()` annotates, `for_export()` calls it and chains
the prefetches (`managers.py:143`) — and the export resource reads the second
(`resources/export.py:396`).

**Decision**: SC-001 and SC-002 are proven against the complete row, which means after FR-007's
method for the child and after FR-010's for the parent. FR-004 and FR-008 are proven separately
against the scalar set alone.

This is a reading of the specification rather than a change to it, and it is recorded here because
a reader could take SC-001 to mean the annotating method alone, and would then write a test that
cannot pass.

## R4 — Three published columns that resolve to nothing, and which of them is this feature's

**Question**: which columns render empty on every row, and why.

**Findings**

Three, and they are not the same case.

- **`Ref_IGSN`** — settled. The portal holds no sample numbers by decision, the column stays and
  stays empty (`decisions.md`, D3).
- **`publication_reference`** and **`data_reference`** — the admin reads
  `obj.publication_references` and `obj.data_references` through `getattr(..., None)` and returns
  an empty string when absent (`admin.py:295,302`). Neither attribute exists. `HeatFlow`'s field
  set, dumped at runtime, is: `M_score`, `U_score`, `added`, `c_comment`, `contributors`,
  `corrections`, `dataset`, `date_acquired`, `dates`, `descriptions`, `expedition`, `ghfdb_id`,
  `id`, `identifiers`, `image`, `is_relevant`, `keywords`, `local_id`, `measurement_ptr`,
  `method`, `modified`, `name`, `options`, `parent`, `polymorphic_ctype`, `quality`, `sample`,
  `tagged_items`, `tags`, `thermal_conductivity`, `thermal_gradient`, `uncertainty`, `uuid`,
  `value`, `water_temperature`. There is no reference relationship on it.

The two reference columns are a real gap with a home on the roadmap: R5 requires the correct
literature attached to each record, resolved against existing bibliographic records. Until that
lands there is nothing for these columns to read.

**Decision**: all three columns are present and empty, and this feature builds no reference
relationship. The difference is that one is settled and two are waiting, so the two are filed
rather than absorbed. The `getattr(..., None)` guards are replaced by the same explicit
"nothing resolves this yet" treatment `Ref_IGSN` gets, so that a reader cannot mistake a defensive
guard for a working accessor.

**Checked and not a gap**: `geo_lithology` and `geo_stratigraphy` do resolve. `HeatFlowInterval`
carries `lithology` and `stratigraphy` from its geographic base class, confirmed at runtime, so the
two admin accessors that read them work as written.

## R5 — The parent changelist reads relationships one column at a time

**Question**: the parent flattening method has no caller (`managers.py:233`). What is currently in
its place?

**Findings**

Fifteen display methods on the parent admin walk the relationship chain per column — `get_elevation`
reads `obj.sample.heatflowsite.elevation` through two `getattr` guards, and `get_environment`,
`get_total_depth_md`, `get_country` and eleven others do the same
(`admin.py:596-675`). The changelist's `get_queryset()` calls `select_related` on the same paths
(`admin.py:685`), so this is not an N+1 — it is the same data reached twice as expensively as it
needs to be, in fifteen near-identical methods.

The child admin does not do this. It reads annotations through the `_scalar()` factory.

**Decision**: the parent changelist reads the parent flattening method, as the child changelist
reads the child's. That makes the unreferenced method reachable and testable, removes the fifteen
methods, and makes the two admins the same shape — which is what lets one mapping and one factory
serve both.

Two annotation names need care. `site_name` avoids a collision with the `name` field the framework's
base class declares, and `quality_parent` is the published name for a field called `quality`.
FR-011 covers the first. The second is the mapping's job, not the queryset's.

## R6 — Scoping survives chaining, and where it can be lost

**Question**: FR-002 requires the published-identifier restriction to hold on every route, and
SC-005 requires it proven on a chained queryset and on the changelists.

**Findings**

Both managers apply the filter in `get_queryset()` (`managers.py:182,283`), so it holds for anything
derived from the default manager. Two routes bypass it.

`Model._base_manager` is used by Django internally for related-object lookups and by the admin for
`get_object()`. It is not the default manager, so it is unfiltered. This matters for the admin's
detail and delete views, which the changelists do not expose (FR-012), but it means a scoping test
that only exercises `objects` proves less than it appears to.

`_default_manager` is what the admin changelist uses, and the admin's own `get_queryset()` overrides
it explicitly in both admins, so the scoping there is inherited from the manager call the override
makes rather than from Django. A future edit to either override could drop it silently.

**Decision**: SC-005 is proven at three points — the manager, a chained queryset, and each
changelist's rendered rows — rather than at the manager alone. The changelist assertion is what
would catch an override that stopped going through the scoped manager.
