# Implementation Plan — 003 a published release read into the portal

**Specification**: [spec.md](spec.md) · **Decisions**: [decisions.md](decisions.md) ·
**Research**: [research.md](research.md)

**Written**: 2026-08-24, after the specification was agreed.

## Context

The portal can write the published structure out of its model and cannot read a release in. The
existing import path reads a spreadsheet the community fills in, not the file a release is
distributed as, and it was built against a hand-made fixture that matches the code rather than the
format. This adds the reading direction for a release, through the administrative interface, and
lands the file as one dataset for each publication that reported the data.

Three properties carry the feature, and each is a separate kind of work:

1. **Nothing is written unless the whole file passes.** Mostly a matter of correcting what the
   library does by default, which is the opposite (R5).
2. **The file becomes datasets and literature as it is read.** New behaviour with no precedent in
   the codebase.
3. **A row becomes the records the portal keeps.** Present in outline for the other format, and
   reusable at the widget layer only.

## Technical context

- Django 5.2 on Python 3.13, FairDM, `django-import-export` 4.3.9.
- `heat_flow` owns the model, `ghfdb` reads and writes the published structure. The dependency
  points one way and this feature does not reverse it.
- The published column definitions live in one module already and stay the single source of truth,
  extended to describe the release format's own columns (FR-007).
- Tests mirror the source tree, one factory per model, fixtures in `conftest.py`, tests grouped in
  classes.

## The three structural decisions

### One resource, not two

The existing path splits parent and determination across two resources the curator runs separately.
A release row carries both halves and has to produce its dataset, its literature, its site, its
interval and its determination together, so it is one resource reading one row into everything that
row describes.

This is not a change to the existing pair. They read the other format and keep it. What the two
paths share is the widget layer and the column definitions.

### Header validation empties the dataset

There is no hook that aborts before the first row (R3). Raising in `before_import` is caught, the
error is recorded, and every row is then read anyway. The check therefore records what is wrong and
empties the dataset, which the library re-measures immediately afterwards for exactly this purpose.

The consequence to design for: the fault has to be reported from `result.base_errors`, since no row
result will exist.

### The all-or-nothing guarantee is an override, and needs its own test

On the confirmed pass the library commits the valid rows and skips the refused ones, and then
reports success without looking at the result (R5). That is precisely what the specification
forbids, and it is the default, so it will pass any test that only exercises a clean file.

`process_dataset` is overridden to roll back on validation errors, and the confirmed pass's result
is checked before anything is reported as done. Both get a test that reinstates the default and
proves it fails.

## Approach, by story

### US-1 — a release file is checked in full before anything is written

The reading format is a thin subclass of the library's comma-separated format. The layout needs no
other change: the release's header is on line 1, which is what the library already assumes.

**Where it is registered, and what that reaches.** The release format and its resource attach to the
determination changelist, which already carries the import machinery and already gates on the
permission to add records — which is what FR-001 asks for, and what the two closed permission tasks
were closed against. The site changelist is not a candidate: a release row carries both halves.

That choice has a consequence to state plainly rather than discover. The rollback correction and the
result check are properties of the registration, not of one resource, so they also reach the
contributor template's reader on the same changelist. **This is intended.** That reader declares the
same guarantee today in a form the library ignores, so its imports commit their valid rows and skip
their refused ones while reporting success — raised as its own issue during the audit. Correcting it
here costs nothing extra and leaves no known way to half-write an import behind.

The same reasoning covers the vocabulary correction in US-3: the widget it fixes is shared, so
making a many-valued vocabulary failure fatal changes the contributor path too. Rows that import
today with a silently empty relation will be refused instead. Also intended, and for the same
reason — the alternative is a release-only subclass that leaves the defect live on the other path.

Header validation runs in `before_import` and compares the file's headers against the release
format's column set, three ways — a misspelled published name, a name the format does not define,
and a required name that is missing. Each names the offending column. Any failure empties the
dataset.

Value checking is already exhaustive by default: the row loop only stops early when `raise_errors`
is set, and the administrative path leaves it false. So FR-009 needs no code, and gets a test that
would catch a later regression.

Reporting needs two corrections. A widget raises `ValueError` rather than `ValidationError`, because
the library re-tags the former with the field and loses the latter's field entirely. And the row
number the library reports counts data rows, so it is one less than the line the curator is looking
at in the file; the reader is given the file's line number.

### US-2 — the release lands as one dataset for each publication

`before_import` resolves the whole file's publication references once, before any row is read: it
collects the distinct references, matches each against the portal's bibliographic records, creates
one where none matches, refuses where more than one does, and creates the dataset. The map it builds
is held on the resource for the row pass.

Comparison ignores case and surrounding whitespace. The reference each dataset came from is stored
on the dataset rather than left to be recovered later, through the dataset's existing one-to-one
link to a bibliographic record — the citation key is then one hop away and no model change is
needed, which is what the constitution check below asserts.

The hook runs on both passes against different instances, and the dry run's writes are rolled back,
so nothing may carry a primary key from one pass to the next.

### US-3 — every row becomes the records the portal keeps

Per row: the site, its parent heat flow value, the interval, the determination, the gradient, the
conductivity, the corrections the row supplies and, where the row supplies it, the probe metadata.

The interval is the part with no column of its own. It is identified by its site together with the
depth range, and where the row gives no depth it is the site's one indeterminate interval. A site
may hold both kinds at once.

Where two rows disagree about a record they share — a site's coordinates, an interval's probe — the
file is refused and the disagreement named. In the current release this is 974 intervals, so it is
the ordinary path and not a defensive corner.

The widget layer is reused as it stands for vocabulary normalisation and quantity parsing, with two
corrections the audit found: a vocabulary failure on a many-valued column is currently caught and
discarded, and a correction flag currently bypasses the normaliser so a bracketed flag is lost.
Both are defects against this specification and both are fixed here.

### US-4 — importing the same file twice changes nothing the second time

Falls out of the identities above rather than needing machinery of its own: the determination is
found by its published identifier, the gradient and conductivity by the determination's, the
corrections by their determination and type, the interval by its site and depth range, the site by
its published identifier.

The one piece of real behaviour is the site's dataset. A site belongs to the earliest publication
year among its determinations, compared as each import runs, so a later import carrying an earlier
publication moves the site and leaves its determinations where they are.

## Sequencing

**US-1 lands in two parts, and this matters.** Its first part — the header check and the two
corrections to how a fault is reported — comes first and alone, because it needs no record to be
written and everything downstream depends on a bad file being refused.

Its second part is the all-or-nothing guarantee, and that cannot be proved until rows write
something. A test asserting "one refused value writes nothing" passes vacuously against a reader
that writes nothing at all, which is the same shape the reconciliation rejected a proposed closure
for. So those tasks sit at the end of the implementation, after US-3, and close US-1 from there.

US-2 and US-3 then run together — a row cannot be filed without its dataset and a dataset is not
observable without rows, so splitting them would make both halves' tests indirect.

US-4 last, because it asserts about the state two imports leave behind and needs the rest to exist
before it can say anything.

## Constitution check

- **II, schema fidelity.** The published column definitions stay the one source of truth and grow to
  describe the release format. No published name is invented, altered or accepted misspelled.
- **III, FairDM first.** Datasets, samples, measurements and bibliographic records are the
  framework's own; nothing is reimplemented beside them. No model change is required — the two
  relationships this feature leans on already exist as needed.
- **VI, test first.** Every task lands its test before its code, and the two tasks that correct a
  library default reinstate the default to prove the test fails without them.
- **IX, simplicity.** One resource for one file, sharing the widget layer with the path that already
  exists rather than generalising either into the other. The contributor template's reader is a
  later feature and this one is not shaped in advance to accommodate it.
- **Quality is computed here.** The supplied quality code is recognised and discarded.

## Convergence

The feature converges when a file of known rows imports to known records, a file with a known fault
is refused with that fault named by row and column, the same file imported twice leaves one copy of
everything, and the portal is unchanged after every refusal.

The fixture is the load-bearing part. The existing one imitates the code; this feature's is cut from
the real release file, so that what the tests exercise is the format the portal will actually be
given.
