# Decisions — 003 a published release read into the portal

The specification in this directory was written in April 2026 and rewritten in place on 2026-08-24
after an audit against the code. This file records what the audit found and how each disagreement
was settled, so the rewrite can be read against the original rather than replacing it silently.

Git history holds the original text. Nothing here is a substitute for reading it.

## How the audit ran

Every requirement in the original specification was checked against the implementation and sorted
into four groups: still true, drifted, absent, and behaviour the code has that the specification
never mentioned. The task list is then rewritten as though no code existed and reconciled against
the codebase afterwards, so that what the feature is missing is measured against what it should
have been rather than against what was built.

The original `tasks.md` recorded 79 of 79 tasks complete. That is a claim the file makes about
itself, and it was not treated as evidence of anything.

The original had **no requirements section and no success criteria section at all**. It cited a
requirement, `FR-016`, that appears nowhere in the document. Above its overview sat nineteen lines
of dated amendment stamps carrying nine defect reports, each written into the specification instead
of into an issue, several of them amending an earlier amendment. The rewrite carries the final
reading only, and the defect stamps are gone — see D12.

## Settled

### D1 — The round trip is split, and this specification is the reading half

**Original**: one specification covering import and export together, on the reasoning that "the
round-trip is only complete when export is working".

**Code**: import works in outline against a format nobody publishes. Export produces values but
cannot produce a file a curator could submit — a third of the published columns emit under the
wrong header or not at all, which the repository's own suite records as expected failures under
issue #122.

**Ruled**: split. Import is what the portal needs now, and every open question on this subject is
on the export side. #122 asks which spelling of the published column vocabulary is canonical, and
nothing about reading a file depends on the answer. Export becomes `004` and takes #122 with it.

The cost was weighed and is small. Export is the only honest check on whether an import was
faithful, but its failure is in headers, ordering and completeness rather than in values, so the
existing round-trip check keeps working while export waits.

**Consequence**: R3 splits. It keeps the reading half and becomes this feature; writing a release
out becomes R17, which is where `004` lands. R5's deliverable "confirmation that a release exported
after the import carries the same data as the release that went in" moves there too, since it
cannot be demonstrated without a working export. The community upload template was also part of R3
and belongs to R6, which already covers uploading a completed template file.

R3 had been recorded as delivered, and was not. The audit found that nothing in the code can read a
published release: it is a comma-separated file with one header row, and both importers read a
spreadsheet with its headers on the sixth. The tag came off in the same change that split the item.

### D2 — The release import and the contributor upload are separate specifications

**Original**: silent on the distinction. It described "a GHFDB-format XLSX file exported from the
official IHFC spreadsheet template" as one thing.

**Code**: two import formats exist, both reading a spreadsheet with headers on row six. Neither can
read a published release, which is a comma-separated file with headers on row one.

**Ruled**: separate. They share most of their reading — the same vocabulary handling, the same
model, the same reporting — but they are different files with different layouts, and only one of
them matters now. The release import is this specification. The contributor upload becomes `005`
under R6, and inherits the reading this one builds.

### D3 — The specification is replaced in place, keeping its number

**Original**: `003-ghfdb-import-export`.

**Ruled**: rewritten in the same directory, renamed `003-ghfdb-release-import` because the old name
describes a scope this no longer has. The epic already raised for it is reused rather than a second
one opened for the same subject. A second copy on disk would be a second thing for a reader to find
and believe.

### D4 — One dataset for each publication reference

**Original**: silent. The original importer had no concept of a dataset at all.

**Ruled**: each distinct publication reference becomes one dataset, titled from the title of the
bibliographic record it resolves to. This is not new doctrine — `CONTEXT.md` already states that one
publication is always one dataset — but nothing in the reading path implemented it.

The current release carries 1,586 distinct publication references across its rows, none of them
empty, the largest covering 16,046 rows and 134 appearing exactly once.

### D5 — A missing bibliographic record is created; an ambiguous one is refused

**Original**: silent.

**Ruled**: where a publication reference matches no bibliographic record, one is created carrying
the citation key. The portal's bibliographic records require only a citation key and a type, so a
record holding nothing else is valid and can be completed later by whoever assesses it.

Where a reference matches more than one record, the rows carrying it are refused. Citation keys are
explicitly not unique in the portal's own records, so a match of two is a real possibility, and
choosing between them would attach a determination to a publication on a guess.

### D6 — A site reported by two publications belongs to the earlier one

**Original**: silent. The original had no dataset concept, so the question could not arise.

**Evidence**: 4,817 of the release's 71,934 sites carry determinations cited to more than one
publication. Site identity itself is unambiguous — every site has exactly one pair of coordinates.

**Ruled**: the site belongs to the dataset of the earliest publication year among its determinations.
Its determinations do not move; each stays with the dataset of the publication that reported it.
This matches how the framework describes the relationship, as the dataset a sample first appeared
in.

Ownership is compared as each import runs and reassigned when an earlier publication arrives later,
rather than resolved from the whole file in advance. The comparison then holds however the work is
divided, which resolving in advance would not.

### D7 — Misspelled published column names are refused, without exception

**Original**: silent on the header check. The importer's own concern was the opposite — suppressing
errors about columns that were *absent*.

**Code**: no check exists. The published names the portal treats as correct are held in one module,
and the misspelled forms appear nowhere in the reading path.

**Finding**: the published 2024 release carries both misspelled names in its header, and neither
correct spelling appears in it. Read literally, the standing rule refuses the exact file this
feature exists to read.

**Ruled**: the rule holds, unchanged and without an exception. The import refuses the file before
reading any data row, and the refusal is covered by tests that assert it. Correcting an outdated
header is part of preparing a file for import, alongside dividing it — the operator's step, not the
portal's.

This is settled and closed. Perpetuating a spelling error because a file contains it is what would
make the error permanent, which is what ADR-0003 exists to prevent.

### D8 — The import is administrative, and the confirm step is the check

**Original**: "All import/export actions are staff-only via the Django admin."

**Ruled**: unchanged, and for a better reason than the original gave. The administrative import
already validates every row, writes nothing, and reports failures with the row and the field
attached — which is exactly the checking this specification requires. A separate command would
rebuild that machinery, and a curator correcting a file would need shell access to use it. One
reading path also serves both this feature and the contributor upload that follows.

A command was considered and rejected. The argument for it was the size of a release file, and
size is explicitly not this feature's concern.

### D9 — Nothing is written unless the whole file passes

**Original**: "The importer collects these as validation errors and rolls back the entire import,
reporting all such rows together." Stated only as an edge case, for missing mandatory fields.

**Ruled**: promoted from an edge case to the feature's central guarantee, and widened to every kind
of failure rather than missing values alone.

The reasoning offered during the audit — that the file profiles clean, so a refusal probably
indicates a fault in the reader — was rejected. A profile only measures the checks somebody thought
to run. A refused row means the data is probably wrong, the file is corrected at source, and a
seeding is dry-run before it is run for real.

### D10 — Identity is the published identifiers

**Original**: the published identifiers map to `local_id` on the determination and on the parent.

**Code**: they map to `ghfdb_id` instead. `local_id` is written only on the site, and the natural
key computed when the identifier columns are absent is stored in the determination's *name*.

**Ruled**: the published identifiers are the identity, and the field holding them is the one named
for them. `002` settled that this field is the record's own published identifier and is not itself
a published column. Storing a computed key in a name field is not identity, and it goes.

The fallback that computed a key from coordinates when the identifier columns were absent goes with
it. A release always carries both identifiers, and the contributor template — which does not — is a
different specification.

### D11 — A vocabulary failure is never silent

**Original**: "a descriptive validation error is raised identifying the row number, column name, and
invalid value."

**Code**: two failures against that. The error names the value and the vocabulary but neither the
row nor, for most columns, the column. And for every many-valued column — the lithology, the
stratigraphy, each temperature method, each conductivity column, the exploration purpose — the
error is caught and discarded, so a row carrying an unrecognised term imports clean with the
relationship left empty.

**Ruled**: the original is right and the code is wrong, on both counts. Most of the vocabulary
surface of a release is many-valued, so discarding those errors discards most of the checking this
feature exists to do.

### D12 — Defect reports leave the specification

**Original**: nine defect reports written into the header as dated amendment stamps, several
amending an earlier stamp, one narrowing the scope of the stamp above it.

**Ruled**: none survive. A specification says what the feature must do. A defect says what the code
did wrong on a particular day, which belongs in an issue and then in the history. Where a stamp
carried a genuine requirement it is now stated plainly among the requirements, and where it recorded
a fix to something the rewrite no longer describes, it is gone.

Two are worth naming for the reader of the original. The stamps about the synthetic keys that were
never to reach a curator's screen describe a mechanism the code no longer has — the keys are not
generated, so they cannot leak. The stamp requiring the published column vocabulary to be adopted
throughout was half-carried-out, and what remains of it is `004`'s.

### D13 — What the file supplies and the portal does not keep

**Original**: silent. The original described a spreadsheet the portal had never actually read.

**Ruled**: a release carries columns beyond the determination and site columns — the identifiers,
the publication year, a computed quality code, geography, and the assessment team's own columns.
Each is either read, or recognised and not stored, and the specification says which.

The quality code is recognised and discarded, by standing constraint: the portal computes quality
from what it holds and does not ingest supplied codes. The assessment columns are recognised and
discarded because recording assessment in the portal is aspirational and no field waits for them.
Neither may cause a file to be refused, since both are part of the format.

### D14 — Rows are never dropped, and names are never judged

**Original**: silent on both.

**Code**: two behaviours nothing asked for. Rows sharing a site are deleted from the file as it is
read, with no count and no notice, so the confirmation a curator sees cannot match the file they
uploaded. And a site whose name is a number is refused, while a site whose name is empty produces a
site with neither name nor location.

**Ruled**: both go. Every data row is either imported or reported as refused, and nothing else may
happen to it. A site's name is a label, not a key — 11,513 sites in the current release are named
`?` and 10,898 are named with a number — so a name is stored as given and never causes a refusal.
Where two rows genuinely disagree about a site they share, that is reported rather than resolved,
per the standing constraint that the portal does not guess at supplied data.

### D15 — An interval is a sample, and is shared by every determination measured over it

**Original**: silent. The original importer created an interval per row without saying so.

**Evidence**: 8,145 intervals in the current release carry more than one determination, covering
21,722 rows — a quarter of the file. Of those groups, 68 per cent differ on the determination's own
heat flow value and 49 per cent were reported by different publications.

**Proposed and rejected**: that each determination own its own interval. It would have made every
dependent record reachable from the determination's identifier, which is the whole difficulty this
decision exists to solve, and the file offers no interval identifier of its own.

**Ruled**: rejected, because it is wrong about what an interval is. An interval is a sample in its
own right, and it can be sampled again — a heat flow derived from a fresh conductivity or gradient
over an interval another team measured is measuring the same thing, and must attach to the same
interval. Modelling one interval per determination would record two samples where the science has
one.

So the interval is identified by its site together with the depth range the row gives, and is
shared.

### D16 — The gradient and the conductivity take the determination's identifier

**Original**: silent.

**Ruled**: a row is a determination together with the gradient and the conductivity it was derived
from, so both take that row's determination identifier.

The question this answers is how a re-derived determination is told apart from a newly added one.
It is not: the file records no such distinction, and does not need to. Both arrive as a new row with
a new identifier over an interval that already exists, and what separates them is which publication
reported each — which the portal already records, because each publication is its own dataset.

Identifying the gradient and the conductivity by the determination records what the file states
rather than inferring what it does not. Nothing in a release says two rows report one gradient
*record*, and 43 per cent of shared-interval groups give different gradients while 31 per cent give
different conductivities. The alternative — matching on the value — is the proximity matching the
standing constraints rule out.

The consequence worth stating: every dependent record except the interval is now reachable from the
determination's identifier, which is what makes repeating an import deterministic.

### D17 — Rows with no depth attach to one indeterminate interval per site

**Original**: silent.

**Evidence**: 4,687 groups covering 13,153 rows give neither a top nor a bottom depth. Within them,
74 per cent carry different determination values, and the site's total depth agrees in all but 21
groups.

**Ruled**: they attach to a single indeterminate interval for that site, understood as covering the
whole borehole or probe deployment, with several determinations relating to it. A site may hold that
interval alongside intervals with real depth ranges; they are different samples and are not merged.

### D18 — Probe metadata stays on the interval, and disagreement is a refusal

**Original**: silent.

**Code**: probe metadata is held once per interval, as a one-to-one relationship.

**Proposed and rejected**: moving it to the determination, on the grounds that 7,540 shared
intervals carry more than one row bearing probe metadata and the second row's has nowhere to go.

**Ruled**: rejected. For a marine measurement the probe describes the interval being sampled, and
there is no reason it would differ between determinations over that interval. The relationship is
right and the data is what disagrees: 974 of the 8,145 shared intervals hold rows that contradict
each other about the probe, 878 of them on the probe type alone.

Those rows are refused and reported, like any other disagreement about a shared record, and
corrected at source. This is the general rule of D9 applied to a case that turns out to be ordinary
rather than remote.

### D19 — Foundations Implementer notes (T001-T005, T007)

The plan and the task list name what each Foundations task delivers but not every file name or
internal boundary. Recorded here, not as design decisions binding a later story, but as the
Implementer's own record of the non-obvious choices this phase made while staying inside its named
scope (constants.py, the test module, the fixtures, the conftest that exposes them).

**T001 — the test module's name.** Neither the plan nor the task names the file. `test_release.py`
mirrors `project/ghfdb/resources/release.py`, the resource name "one resource, not two" (plan.md)
implies without stating — a release row produces its dataset, its literature, its site, its
interval and its determination together, so one resource reads one file. `release` also matches the
vocabulary the spec, CONTEXT.md and this feature's own name already use throughout.

**T001 — what "collects" requires.** Measured directly: a module with a docstring and
`pytestmark = pytest.mark.ghfdb` but no test function collects zero items under `pytest
--collect-only`, with or without `-q`, in this repo's configuration — probed by creating and
deleting a throwaway file (`test_empty_probe.py`) before writing anything real. So "a new test
module... is named in the collection" needs at least one genuine, non-tautological test, not a bare
marker declaration. `test_carries_the_ghfdb_marker` proves the module's own claim to the marker
using `request.node.get_closest_marker`, rather than asserting something trivially true of the
two lines just above it.

**T002 — `RELEASE_COLUMNS` folds in the two misspelled names.** T003's own acceptance text says the
three-way split's union "is the release column list," and FR-007 requires the header check and the
row reading to consult one place, not two. Appending `MISSPELLED_COLUMNS`'s keys to
`RELEASE_COLUMNS` is what lets `REFUSED_COLUMNS` be a subset of it — otherwise the union claim in
T003 and the "one place" requirement in FR-007 would need two collections, contradicting each
other. This also means `RELEASE_COLUMNS` carries `ID_parent` twice (once from `PARENT_COLUMNS`,
again from `RELEASE_ONLY_COLUMNS`, since the two identifiers the release format's own R1 measurement
names — `ID_parent` and `ID` — are conceptually release-only additions even though `ID_parent` was
already present in the pre-existing `PARENT_COLUMNS` for the unrelated changelist-mapping purpose
`columns.py` built it for). T002's own acceptance test (a prefix check plus an exactly-once check on
`CHILD_COLUMNS`) does not exclude extra entries, so the duplicate is harmless to both tests and to
every consumer that treats `RELEASE_COLUMNS` as a set. **Revisit if** a future task consumes
`RELEASE_COLUMNS` positionally (e.g. as a literal export column order) rather than as a name set —
at that point the duplicate needs resolving explicitly rather than left to collapse.

**T003 — `quality_parent` and `quality_child` are discarded, not read.** FR-033 names only the
release-wide `Quality_Code`. `quality_parent` and `quality_child` are two more names already present
in `PARENT_COLUMNS`/`CHILD_COLUMNS` (built for the existing changelist-display path, not this
feature), and R1 measured both as permanently absent from a real release, "the portal computes
quality, so their absence is correct rather than a gap." Standing constraint 3 ("quality is computed
here") reads as covering every quality-shaped column, not only the one FR-033 happens to name by
example, so both join `DISCARDED_COLUMNS` alongside `Quality_Code`. **Revisit if** a future story
finds a release genuinely carrying either with a value the reader is expected to consult — nothing
in R1 or the FRs anticipates that, but the assumption is mine, not the spec's.

**T004/T005 — the base fixture keeps both real misspellings; the corrections happen in T005.**
T004's own acceptance test is literal and unambiguous — "the fixture's header equals the release
file's header read from the archive" — which only holds if the base keeps `tc_pT_fuction` and
`Ref_ISGN` exactly as downloaded. SC-001 separately requires proving the misspelled-header refusal
"for each misspelled name," independently, "so that a check keyed to one cannot leave the other
unrefused" (T011) — which the base alone cannot demonstrate, since it always carries both together.
T005's two misspelled-header variants resolve this: each corrects exactly one of the two published
names, leaving the other misspelled, isolating the two refusal cases the way SC-001 asks for.

**T004 — the fixture's rows.** Cut from site `R24-P003477` (6 of the 7 rows) plus one row from
`R24-P004314` (for a literal `[Unspecified]` cell — none of `R24-P003477`'s rows carry one).
`R24-P003477` alone gives rows sharing a site, rows sharing an interval with agreeing (not yet
disagreeing) depth and probe values, rows with no depth, and four distinct publication references —
found by scanning the archive programmatically for a site combining all of those shapes in the
fewest rows, rather than assembling them from unrelated sites. The interval-sharing pair
(`R24-033563`/`R24-053075`) was chosen specifically because both already agree on `probe_type`,
which T005's disagreement variant needs — a pair that already disagreed in the real data would leave
nothing for that variant to change.

**T004 — the fixture's line endings follow the repository's own normalisation, not the archive's.**
The archive uses CRLF; `.gitattributes`' repository-wide `* text=auto` (pre-existing, not this
story's) normalises every text file to LF on commit, and the fixture, once staged, is no exception
— confirmed directly: `git cat-file -p` on the committed blob shows zero CRLF sequences where the
pre-commit working copy had eight. "Byte-for-byte" here is read as binding the header text, the
column order, the byte-order mark and every field value — everything T004's own wording names — not
the row-terminator convention, which is a repository-wide policy this story neither owns nor should
carve an exception into. `read_csv_rows`/`read_csv_header` use `str.splitlines()`, which treats CRLF
and LF identically, so no test in this module depends on which one the fixture carries.

**T005 — the variant fixtures.** `header_missing_required_column.csv` and
`header_undefined_column.csv` change the header line only, leaving the data rows exactly as the
base fixture has them — deliberately, since FR-003 and the plan both describe the header check as a
pass over header names alone, before any row is read, so a header/row shape mismatch in these two
variants is never actually consumed. The four row-level variants (`bad_vocabulary_value`,
`numeric_value_in_text_column`, `disagreement_shared_site`, `disagreement_shared_interval_probe`)
each change one field on one row, verified programmatically against the base fixture (parsed with
`csv.DictReader`, keyed by `ID`, diffed field by field) before being committed, and that same
single-field-diff property is what `test_single_row_variant_changes_exactly_one_cell` asserts.

**T007 — the ambiguous-citation-key fixture differs by case and whitespace, not identical strings.**
`literature.LiteratureItem.citation_key` is unique at the database level (upstream), so two rows
cannot literally share one string. FR-017 requires publication-reference comparisons to ignore case
and surrounding whitespace, so two citation keys differing only that way are "one reference" by the
spec's own rule while remaining two distinct, independently-identified database rows. The fixture
and its test build that pair and confirm both properties hold, without pre-empting US-2's own
matching implementation.

**Restructuring — the test module moved from `test_resources/test_release.py` to
`test_ghfdb/test_constants.py`, discovered by the mandatory full `forge verify`, not by inspection.**
The repo's conformance gate (Article X, mechanical) requires every test module to mirror an existing
source module. `tests/test_ghfdb/test_resources/test_release.py` mirrored
`project/ghfdb/resources/release.py` — the resource this phase deliberately does not create, since
it is US-1's T009 — so the gate failed: "mirrors no source module." The tool provides a
`[tool.forge.conformance] non-mirror-paths` declaration for genuine "no source module by design"
cases (a Cotton/template test suite, per the tool's own docstring), but this is not that: the module
*will* exist, one story later, and declaring a permanent exemption for a temporary gap would need
walking back the moment T009 lands — a stale declaration nobody would remember to remove.

Renaming and relocating the file to mirror `project/ghfdb/constants.py` instead — the module every
constant this phase adds actually lives in — passes the gate honestly, with no source module
invented ahead of its story and no config exemption to reconcile later. T007's two fixtures moved
from `tests/test_ghfdb/test_resources/conftest.py` (their original home, chosen because a future
US-2 resource test would look for them there) up to `tests/test_ghfdb/conftest.py`, since a fixture
consumed by a test at `tests/test_ghfdb/test_constants.py` needs a conftest at or above that level to
be visible — still "the conftest that exposes them," the brief's own phrase, just the ancestor
conftest rather than the descendant one. Nothing in the six tasks' content changed; every test,
fixture and assertion is unchanged from what T001-T007's own progress.md entries describe. **Revisit
if** T009 creates `project/ghfdb/resources/release.py` and its own test module — at that point the
constants-only tests in `test_constants.py` and the resource tests in a new `test_resources/test_release.py`
are two different subjects and should probably stay split as they are now, but a reader landing here
after T009 exists should not be surprised to find `RELEASE_COLUMNS` tested somewhere other than
beside the reader that consumes it.

### D20 — US-1 first part Implementer notes (T008, T009, T011-T024, T033)

Recorded for the same reason as D19: not design decisions binding a later story, but the choices
this phase made while staying inside its named scope (the reading format, the header check, the
value-reporting corrections, the anonymous-access proof) and the ones a later story needs to know
about before building on top of them.

**T008 — "the real header" is the corrected header, not the archive's.** Taken literally against
D7, this looks contradictory: the base fixture (`release_sample.csv`) carries both misspelled names
because it is cut byte-for-byte from the real file, and D7 rules that the import refuses that file
without exception. T008 cannot mean "the fixture, unmodified, passes" without reopening D7. Read the
other way — "the file a curator would submit after preparing it," which is exactly the phrase D7's
own ruling uses — the two are consistent: T008 exercises a header with both published names spelled
correctly, built in the test module by mapping `MISSPELLED_COLUMNS` over the base fixture's real
header and rows (`_corrected_header_and_rows`), not a new fixture file. No Foundations fixture is
"corrected" by design (D19, T004/T005), so this construction happens once, in `test_release.py`,
and every later test in the module that needs a clean starting point calls it.

**T009 — `get_title()` cannot simply return a curator-facing string.** `TablibFormat.create_dataset`
(the base `CSV` format's own implementation) passes `get_title()` to `tablib.import_set(...,
format=...)` as the *lookup key* into tablib's own format registry — "csv" is both this format's
internal registry key and, for the unmodified base class, its displayed title. Overriding
`get_title()` to return "GHFDB Release Format" (T009's own requirement — a name a curator can
recognise) breaks that lookup with `UnsupportedFormat`. `GHFDBReleaseCSVFormat.create_dataset` is
reimplemented directly against `csv.reader` rather than delegated to the inherited path, keyed off
`TABLIB_MODULE` instead of `get_title()`. The reimplementation also tolerates a data row wider than
the header (truncating the excess) rather than raising `tablib.exceptions.InvalidDimensions` — see
the T015/T016 entry below for why this is load-bearing, not incidental robustness.

**T015/T016 — the reading format has to survive a ragged row, because the fixture built for exactly
this case is ragged.** `header_missing_required_column.csv` (T005) drops one name from the header
line only, per that task's own note ("leaving the data rows exactly as the base fixture has them").
Read through tablib's own `CSVFormat.import_set` (or built by hand via `tablib.Dataset(headers=...).
append(row)`), every data row is one cell wider than the new header and raises `InvalidDimensions`
before the resource ever sees a `dataset` — the row loop never gets the chance to run, let alone the
header check. `GHFDBReleaseCSVFormat.create_dataset`'s row loop pads a short row and truncates a
long one to the header's width, the same tolerance tablib's own reader already applies in one
direction (padding) but not the other. This is not generic CSV robustness for its own sake; it
exists because this exact fixture, unmodified, would otherwise be unreadable, and FR-006 requires a
missing column to be *reported*, not to crash the reader.

**T003's `REQUIRED_COLUMNS` reuses `READ_COLUMNS`, not `READ_COLUMNS | DISCARDED_COLUMNS`.** Checked
empirically before writing the header check: `DISCARDED_COLUMNS` holds seven names, and the real
release archive's header (read via `zipfile` + the corrected column set) carries five of them
(`Quality_Code`, the four assessment columns) but not the other two, `quality_parent` and
`quality_child` — confirming R1's own note in `constants.py`'s docstring that those two "are never
present in a real release." Had the missing-column check treated all of `DISCARDED_COLUMNS` as
required, the corrected base fixture — the file T008 needs to pass cleanly — would itself be refused
for two columns that D13 says are optional wherever they appear. `REQUIRED_COLUMNS = READ_COLUMNS`
resolves this without a special case: a column the reader actually consults is required: a column
it recognises and discards is optional, whichever of the seven a given file happens to carry.

**T011-T024 — the resource maps only `qc` and `qc_uncertainty` to real model attributes; every
other released column is unmapped for now.** The row-checking mechanics this phase corrects — every
fault continuing past the first (already the library's own default), the reported column keyed by
name rather than model attribute, the reported line counting the header — are properties of
`import_instance`/`import_data` and hold for whichever fields are declared, not for any one field in
particular. Wiring the two quantity columns already proven safe by `GHFDBChildImportResource`
(reused, not reinvented, per plan.md "the widget layer is reused as it stands") is enough to
exercise and test all three corrections without pre-building the site/interval/determination mapping
that is US-3's job. Every other released column stays a name in `RELEASE_COLUMNS` the header check
recognises, with no field declared for it yet. **Revisit when** US-3 adds the row-to-record mapping
— `Meta.fields` grows column by column as each one's real target model attribute is decided there,
not here.

**`save_instance` is a deliberate no-op.** `HeatFlow.sample` and `HeatFlow.dataset` are both
non-nullable, and `ModelResource.save_instance` calls `instance.save()` regardless of `dry_run` —
only the outer transaction decides whether that write survives, not whether it is attempted. Without
a real site, interval and dataset to assign (US-2/US-3, out of this story's scope by the brief's own
prohibitions), the library's default `save_instance` would raise `IntegrityError` on every row of
even a fully clean file, which would make T008 unprovable within this story's boundary. Overriding
it as a no-op is what "this story ends at a file being checked and its faults reported" means in
code: nothing is ever attempted, dry run or not, so "no record of any kind is created" (T011) holds
by construction rather than by transaction rollback. **Revisit when** US-3 gives the resource
something real to save — at that point this override is replaced, not merely relaxed.

**`Meta.import_id_fields = ()`.** The library's default, `["id"]`, is silently safe only while no
field named `id` is declared (R3's own finding, re-used here) — but `ModelResource.get_instance`
looks the id-field names up in `self.fields` before consulting the row at all, and `self.fields`
only contains this resource's own two declared fields (`qc`, `qc_uncertainty`), so the untouched
default raises `KeyError('id')` on every row, before either field's widget runs. Explicit empty
`import_id_fields` keeps `_check_import_id_fields` a no-op (its own special-cased comparison is
`== ["id"]` exactly, which an empty tuple also satisfies by falling through both its checks with
nothing to check) and makes `get_or_init_instance` always build a fresh, never-looked-up instance.
Finding a determination by its published identifier so a repeat import updates rather than
duplicates is T100's job (US-4), not this story's.

**T033 — "distinguishably" is answered at `has_import_permission`, not at the HTTP layer.** Every
unauthenticated request to any admin URL, this one included, redirects to the login page the same
way — Django's own `AdminSite.admin_view` wrapper checks `is_staff` before any view-specific
permission code runs, so an HTTP-level test asserting only "anonymous gets redirected" would pass
identically whether or not this route carried a permission check of its own. Measured directly:
temporarily hard-coding `has_import_permission` to return `True` left the HTTP redirect test
passing and the module's own `RequestFactory` + `AnonymousUser` test failing — confirming the HTTP
test alone proves nothing route-specific. The second test calls `has_import_permission` directly
with an anonymous-user request, the same style T031's already-closed staff-without-permission case
uses, so the refusal is shown to be the route's own rather than borrowed from the wall in front of
it.

**Not done: registering the release format and resource on `GHFDBChildAdmin`.** plan.md's own
"Where it is registered" section states the release format and resource attach to the determination
changelist's existing import machinery (`get_import_formats`/`get_import_resource_classes` on
`GHFDBChildAdmin`). Three pre-existing tests not authored in this story assert those two methods'
return values by exact equality against today's single-resource, two-format state
(`test_ghfdb_admin_changelist_refined_configuration`,
`test_it_carries_the_determination_import_resource_and_the_export_resource`, and
`TestAdminGetImportFormats`'s four cases in `test_parent_import.py`) — adding a second resource and
a third format necessarily changes what all of them return. Per this story's own prohibition against
modifying a test not authored in it, none of the three files were touched. `GHFDBReleaseCSVFormat`
and `GHFDBReleaseImportResource` are complete, exported from `project/ghfdb/resources/__init__.py`,
and fully exercised by `test_release.py` — only the admin wiring plan.md describes is outstanding.
Flagged in this run's completion report as a concern rather than resolved unilaterally.

**Deviation: the mandatory baseline `forge verify` (§5 of the brief's rituals) ran after
implementation, not before it.** The brief's rituals name it as the last step, before the tasks
themselves; work began directly from the tasks instead. Caught only when writing this run's
completion report, at which point the tree already carried all seventeen tasks' commits. The
worktree's starting commit (`c3d2352`, the same commit the requester recorded as clean) was never
independently confirmed green in isolation. Mitigated after the fact rather than avoided: no
pre-existing test file was modified at any point in this run (confirmed per-task by diffing each
commit's changed files against the task's declared scope), and the full `forge verify` run at
completion — against the finished tree, all seventeen tasks included — passed every step
(conformance, lint, typecheck, the full suite, build). This does not retroactively prove the
starting commit was green; it does establish that nothing in this run's own commits left the tree
red. Reported as a deviation in this run's completion report rather than silently corrected.

### D21 — The release format and resource are registered when the resource writes, not before

The US-1 first part left the admin wiring outstanding, correctly, and raised the question of when
to do it. It is deferred to the all-or-nothing tasks (T025 to T030), which land after US-3.

Registering earlier would put a working entry in the curator's format list in front of a resource
whose `save_instance` is a deliberate no-op. A curator selecting it would get a run that reads the
file, reports no fault, writes nothing and says it succeeded — a worse state than the feature
simply not being reachable yet, and the same silent-success shape D9 exists to remove.

Two consequences follow, both to be carried out with T025 to T030 rather than treated as blocked:

- `test_ghfdb_admin_changelist_refined_configuration` and
  `test_it_carries_the_determination_import_resource_and_the_export_resource` in
  `tests/test_ghfdb/test_admin.py`, and `TestAdminGetImportFormats`'s four cases in
  `tests/test_ghfdb/test_resources/test_parent_import.py`, assert the two methods' return values
  by exact equality and by count against a single-resource, two-format state. Updating all three to
  the two-resource, three-format state is part of the registration and is authorised here: the
  registry they pin deliberately grows, so the assertions are meant to move with it. This is not a
  test relaxed to accommodate a regression, and none of them may be weakened, skipped or deleted —
  each one keeps its exact-equality shape against the new expected state.
- The rollback correction and the result check reach the contributor template's reader on the same
  changelist, as plan.md's "Where it is registered" already states and intends.

### D22 — US-2 Implementer notes (T034-T050)

Recorded for the same reason as D19/D20: not design decisions binding a later story, but the
choices this phase made while staying inside its named scope (resolving publication references to
datasets and literature) and, this time, the structural overlaps the task list's own decomposition
produced — worth reading before assuming every task's test was observed genuinely red in isolation.

**T034-T036 and T039-T042 share one mechanism, and the task list orders "match" before "create"
while the code could not.** T034 (the first test in this story) exercises five publication
references with no pre-existing bibliographic record, so making it pass at all requires the
create-a-`LiteratureItem`-from-a-citation-key branch (T041/T042's own subject) to exist from the
first commit — there is no reference in T034's fixture for a "match an existing record" branch
(T039/T040) to apply to yet. The task list orders T039/T040 before T041/T042; the dependency runs
the other way. `_resolve_publication_datasets` was built incrementally in the only order that keeps
every commit green and every test's assertion meaningful: create-only (T034-T036), then normalise
the grouping (T037/T038), then add the lookup-before-create branch (T039/T040, which subsumes
T041/T042's "else" as a side effect). T041/T042's own test was written and run against
already-existing code and passed on the first try — flagged, per craft-tdd's own instruction, as
"testing nothing you just wrote" until probed. It was probed (mutating the `else` branch to `continue`,
confirming `LiteratureItem.DoesNotExist`) rather than accepted on faith or skipped; see progress.md's
T041/T042 entry for the mutation and the restore. The same shape recurred twice more and was handled
the same way each time:

- **T047/T048** (the reference reads back off the dataset) is a property of `Dataset.reference`
  that T034-T036's own commit already established — there is no code path that creates a dataset
  without setting it, so a dedicated "storing" task has nothing left to add. Probed by swapping the
  `get_or_create(reference=...)` call for a plain `create()` that never sets it; the new test failed
  as expected.
- **T049** (reusing an existing dataset on a second import) is a property of the lookup-before-create
  branch T039/T040 added — a second `import_data` call queries the real database, not an in-memory
  cache, so it finds what the first call wrote. Probed by forcing the lookup query to `.none()`; the
  second import then hit a citation-key `IntegrityError`, confirming the reuse path is load-bearing.

**T050 could not be probed the same way, and that is itself informative.** Every other "test passed
immediately" case above was probed by disabling the specific branch responsible and confirming
failure. T050 (a dry-run check leaves nothing behind) is not this story's code at all — it is
entirely the library's own guarantee, and confirmed as such rather than assumed from research.md:
`import_export.resources.Resource.import_data`'s own signature computes
`using_transactions = (use_transactions or dry_run) and supports_transactions`, so passing
`use_transactions=False` alongside `dry_run=True` does not disable the transaction — attempted
directly, and the write still rolled back. There is no way to construct a version of this story's
code that would make T050's test fail without also breaking every other test in this run that
depends on a *successful* import committing (which none of them tolerate). The genuine evidence
offered instead is comparative: the identical `_resolve_publication_datasets` code path, run once
with `dry_run=True` (this test, count stays 0) and repeatedly with `dry_run=False` (every other
test in this class, count is always positive) — the same writes, gated only by the flag the library
itself gates on.

**No field was declared for `publication_reference` on the resource, and none was needed.** Per
D20's own note, every released column beyond `qc`/`qc_uncertainty` stays unmapped until US-3 decides
its real target model attribute; `HeatFlow.dataset` exists on the model today; but assigning it from
`import_instance` — even without saving — would be doing US-3's row-to-record mapping under this
story's name, which the brief's prohibitions rule out explicitly. The ambiguous- and
empty-reference refusals in `import_instance` therefore read `row.get("publication_reference")`
directly, exactly the way `_resolve_publication_datasets` does in `before_import`, and write only
to the `errors` dict already keyed by column name — never to the instance. `self._datasets_by_reference`
is built and populated in full (every non-ambiguous, non-empty reference resolves to a real
`Dataset`), ready for US-3 to consume, but nothing in this story reads it back off the instance.

**`Dataset.all_objects`, not `Dataset.objects`, for every lookup and creation in this story.**
`fairdm.core.dataset.models.DatasetManager` (the default `objects`) excludes `PRIVATE` visibility,
and a freshly created `Dataset` defaults to `PRIVATE` (`visibility` field default, read directly from
`fairdm/core/dataset/models.py`). Using the filtered manager would have made T049's reuse silently
fail on every dataset this story itself creates — the exact failure fairdm's own docstring on
`DatasetManager` names `all_objects` as existing to avoid for administrative/import code.
