# Decisions — 001 heat flow data model

The specification in this directory was written in April 2026 and rewritten in place on 2026-08-20
after an audit against the code. This file records what the audit found and how each disagreement
was settled, so that the rewrite can be read against the original rather than replacing it silently.

Git history holds the original text. Nothing here is a substitute for reading it.

## How the audit ran

Every requirement in the original specification was checked against the implementation and sorted
into four groups: still true, drifted, absent, and behaviour the code has that the specification
never mentioned. The task list was then rewritten as though no code existed, and reconciled against
the codebase afterwards, so that what the feature is missing is measured against what it should
have been rather than against what was built.

The original `tasks.md` recorded 67 of 67 tasks complete. That is a claim made by the run that
wrote it and was not treated as evidence of anything.

## Settled

### D1 — Score calculation is not part of this feature

**Original**: the specification deferred the scoring algorithms and kept the stored score fields in
scope.

**Code**: `heat_flow/quality.py` implements the full 2023 scheme — numerical uncertainty and
methodological quality calculators for probe and borehole measurements, perturbation flags, and
assembly of the composite code. Nothing outside that module calls its entry points.
`HeatFlow.get_quality()` returns nothing, and the published value's own accessor delegates to it,
so the composite code is never computed for any record. No test exercises the module.

**Ruled**: the original reading stands. This feature owns the stored fields. Calculation belongs to
the roadmap's quality items and is specified separately.

The scoring methods on the models — the two score accessors on the child determination, the two
`calculate_score()` methods on the gradient and conductivity, and the accessor on the published
value — are a deferred interface awaiting that work, not dead code. They are left exactly as they
stand and the rewritten specification says nothing about them.

### D2 — One published value per site is guaranteed by the application, not the database

**Original**: FR-009 required a `UniqueConstraint` in the model's `Meta` on the sample column.

**Code**: no such constraint exists. Uniqueness is enforced in `save()`. A test written to prove the
database-level guarantee is skipped, with a note recording why.

**Why it cannot be built as written**: `Measurement` is polymorphic, so the `sample` column lives on
the base measurement table rather than on this model's own table. A constraint declared in the
model's `Meta` therefore references a column that table does not have.

**Considered and rejected**: a partial unique index on the base table, restricted to this model's
records. Its predicate would have to hard-code a content type identifier, which is not stable
across databases and cannot be resolved by subquery inside an index predicate. It would work only
on PostgreSQL, leaving development unprotected. And it would catch nothing today: the project
contains no bulk creation, no bulk-mode importing and no queryset-level updates, so `save()` is on
every write path that exists.

**Ruled**: the requirement is rewritten to demand the application-level guarantee, on every write
path including the import path. The skipped test is replaced by one that proves the guard fires.

### D3 — An interval links to its site by an explicit foreign key

**Original**: FR-005 linked an interval to its site through the inherited `sample` foreign key.

**Code**: an explicit `site` foreign key, reachable in reverse as the site's intervals.

**Ruled**: the code is right and the specification was stale. ADR-0001 records the reasoning. A test
pins the field's name and forbids "parent" and "child" appearing in its labels, those words being
reserved for the relationship between measurements. The requirement now describes the foreign key
that exists.

### D4 — The quality field holds a computed code, not an imported one

**Original**: FR-007 and FR-010 introduced `quality` beside `ghfdb_id`, framing both as carried over
from the published spreadsheet.

**Since**: ADR-0004 decided that the portal computes the code from the data it holds, that the
computed value is authoritative, and that a code arriving in a file is rejected rather than stored.

**Ruled**: ADR-0004 governs. The field stays as storage and its provenance is corrected. What fills
it remains out of scope under D1.

### D5 — One site per coordinate pair is enforced, not merely documented

**Original**: the specification says nothing about site identity.

**Since**: ADR-0006 decided that a site is its coordinate pair, one site per pair, with no rounding
or proximity matching.

**Code**: nothing expresses the rule. The import path looks a site up by coordinates before creating
one, but only when the row carries no site identifier — a row that carries one is matched by
identifier alone and can create a second site at an occupied pair.

**Ruled**: enforce it. One site per coordinate pair is a hard requirement for the research team and
has to hold within the application rather than only along one import path.

**How**: the point model already constrains its coordinate pair to be unique, so a pair resolves to
exactly one point record and the rule reduces to the location being unique among sites. Because the
framework declares `location` on the polymorphic sample base, the column lives on the base table and
a model-level database constraint is no more declarable than it was in D2. Enforcement is therefore
application-level, and binds only where a location is set.

### D6 — Deletion behaviour on the gradient and conductivity links is deliberate

**Original**: FR-013 required nullable foreign keys rather than one-to-one relationships, so that
several determinations could share one gradient or conductivity, and said nothing about deletion.

**Code**: both links refuse deletion while a determination references them.

**Ruled**: recorded rather than changed. Refusing the deletion is the correct behaviour for a
measurement another record was computed from, and the specification now states it.

### D7 — The documentation carries a field map and a diagram, both rendering in the built docs

**Original**: the specification treats documentation as out of scope entirely.

**Ruled**: both are in scope, and the field map is checked by a test.

The field map exists and has no tie to the code. Its own text carries a note asking for an automated
mapping test once import and export were implemented, which they since have been, and the canonical
column definitions it would be checked against already exist in the extraction app.

The diagram is written in Mermaid and supersedes the Graphviz sources beside it. Those sources
cannot be rebuilt — Graphviz is not installed — so the images generated from them are frozen
artefacts of a schema that has since changed. Mermaid was not previously rendering either: no
extension is configured for it, so the existing diagram reaches readers as source text.

## Found and routed elsewhere

- **The composite quality code is never computed for any record.** Covered by D1 and belongs to the
  roadmap's quality items. Recorded here because the roadmap marks that work delivered and awaiting
  verification, and this is what verification will find.
- **A publication figure describes a schema the code does not have.** The manuscript diagram and its
  caption in the data model documentation depict a junction table between published values and their
  children, carrying the contribution flag. ADR-0001 records that design as begun and abandoned. The
  figure is a manuscript artefact rather than a stale copy of the documentation diagram, so it is
  left untouched by this feature and raised separately.
