# Decisions — 004 Import a completed upload template into a dataset

Rationale too long to sit inside `spec.md`, plus every ambiguity resolved without asking.

## D1 — The portal's vocabularies are the authority, the template's sheet is not

**Ambiguous because** the upload template ships a `controlled vocabulary` sheet listing permitted
values, and the portal separately holds its own concepts for the same columns. Either could have
been treated as the thing an import validates against, and the sheet is the more convenient of the
two because it travels with the file.

**Chosen**: the portal's concepts decide. The sheet is guidance for whoever fills the spreadsheet in
and is never read by the import. A value the sheet permits but the portal holds no concept for still
refuses the file.

**Defensible because** it is the standing ruling for this portal, given during grilling on
2026-09-10: the vocabularies in the portal app are canon and are what matters. It also has the better
failure mode. Validating against the file lets a stale or edited copy of the sheet decide what enters
the database, which puts the authority inside the artefact being checked.

**Consequence accepted**: the two will disagree, and a file that a data provider believes is correct
will be refused. That is worked out as real datasets are imported, not by reconciliation code
written now.

## D2 — Only failures the portal cannot absorb refuse a file

**Ambiguous because** the template carries three separate contracts of its own: the obligation row
(M/R/O), the allowed-range row, and the vocabulary sheet. Enforcing all three at import would have
been a defensible reading of "validate the file".

**Chosen**: the obligation row and the allowed-range row are not enforced. What refuses a file is a
header that is not the official one, a value the model cannot store, a vocabulary value with no
matching concept, or an empty mandatory model field.

**Defensible because** those two rows are data reporting contracts rather than storage constraints,
and the aim is for a good file to import smoothly with errors raised only where the database or the
application genuinely cannot accept what it is given. They become checks at a later point.

Note the asymmetry with D1: the vocabulary sheet is not a deferred check. It is simply not the
authority, while vocabulary validation against the portal's own concepts is in scope from the start.

## D3 — The official template is the fixture

**Ambiguous because** three spreadsheet fixtures already exist in the test suite and could have been
extended.

**Chosen**: the work is built and tested against an unmodified copy of the published template. The
existing fixtures are hand-built hybrids, and the column constants in the code disagree with the
template on ten names, so the current tests establish nothing about a real upload.

**Defensible because** the feature's whole claim is that the file the assessment team fills in can be
read. A fixture nobody uses cannot support that claim.

## D4 — No revision marker, so the header is the detection

**Ambiguous because** nothing inside the template says which revision of it a file is, so a revised
template that renames, adds or drops a column would be discovered only when a header stopped
matching.

**Chosen**: accepted as-is. The header check is the detection.

**Defensible because** a revision handling scheme has no requirement behind it yet, and the failure
it would guard against is loud rather than silent: the file is refused, naming the header.

## D5 — Roadmap corrections this feature carries

R3 and R5 are struck through, with an ADR recording that the data assessment team ended the release
import direction. R6 gains a note that this feature delivers its programmatic half and the page
follows separately. Recorded here because they are decisions this run took, and they land on this
branch.

## D6 — Three design-review findings, all verified and folded into the plan

The design review ran before any code was written, across compliance, security and architecture. It
returned three blocking findings, each checked against the code before being accepted.

**DR-001, critical.** The plan claimed `ConceptWidget.clean` and `MultiConceptWidget.clean` were the
only places a vocabulary value is interpreted. They are not. Every many-valued vocabulary column
reaches `MultiConceptWidget.clean` through `RelatedModelWidget.set_m2m_relations`, which wraps it in
`except (ValueError, ValidationError): pass` (`resources/widgets.py:294-295`). Thirteen of the
template's controlled-vocabulary columns take that path, so an unrecognised concept in any of them is
discarded and the relation left unset rather than refusing the file. Confirmed in the code. The
swallow is now T028a, and T028b requires the rule's test to use one of those thirteen columns, since
a test written against a single-valued column would have passed over the top of the defect.

**DR-002, high.** `rollback_on_validation_errors` only adds rollback on *validation* errors, and
those come from `Model.full_clean()` only when `Meta.clean_model_instances` is true, which defaults
to false and is set nowhere here. Row errors already roll back without the flag
(`import_export/resources.py:851-855`). So FR-011's fourth fault type, an empty mandatory model
field, had no path to a located fault: it would either write or raise a bare `IntegrityError` naming
no column. Confirmed against the installed library. `clean_model_instances = True` joins T022, and
T026a covers the case.

**DR-003, high.** The child natural key is built from `lat_NS`, `long_EW`, `q_top`, `q_bottom` and
`publication_reference` (`child.py:361-370`), so a resubmitted file correcting a depth interval no
longer matches its own earlier row and writes a second determination. Confirmed in the code. T034 now
names `q_top`/`q_bottom` as the field the test changes, rather than leaving "one changed value" to
chance.

All three remove uncertainty rather than adding architecture, which is the only kind of finding this
stage is meant to produce.

**ADR:** none — these are corrections to a plan before it was built, and the durable decisions they
touch are already covered by D1 and by the stories themselves.

## D7 — The ten disagreements T002 reports: verdicts

T002's test reads the official template's header (row 6, columns B onward) and checks that every
name resolves against `PARENT_COLUMNS + CHILD_COLUMNS + META_FIELDS`. It disagrees on ten names.
None of the ten is a straightforward rename; each is a genuine decision, exactly the possibility the
plan's Risks section named. Judged one at a time:

**`Ref_ISGN` and `tc_pT_fuction` — exception, ADR 0003.** Both are misspellings ADR 0003 already
names as ones the portal corrects: the code keeps `Ref_IGSN` and `tc_pT_function`, and a file
carrying either misspelled form is refused rather than silently mapped (T006). No change to
`constants.py` for these two — the disagreement is permanent and intentional, not something T004
resolves.

**`Country`, `Region`, `Continent`, `Domain` — exception, D8 of `specs/002-ghfdb-proxy/decisions.md`.**
That decision, from the feature that built the admin proxy, already ruled: "they are not published
columns" — geography enrichment fields stored on `HeatFlowSite` (FR-008) and rendered in
`GHFDBParentAdmin`'s changelist after the published block, never through
`PARENT_COLUMNS`. `admin.py`'s own docstring says so directly ("Four geography columns follow it —
portal additions, not part of the published structure (D8)"), and
`GHFDBParentImportResource` already declares pass-through fields for all four
(`project/ghfdb/resources/parent.py`), so the import side already treats them as ordinary spreadsheet
columns — they are simply never one of the *published* ones. Adding them to `PARENT_COLUMNS` would
put them through `ColumnDisplay.list_display_for(PARENT_COLUMNS)` in `GHFDBParentAdmin`, which would
break `test_admin.py::TestGHFDBParentAdmin::test_the_geography_follows_the_published_block` (T100) —
a pre-existing, passing test outside this story's file scope. Left untouched.

**`ID`, `Reviewer_name`, `Reviewer_comment`, `Review_date` — rename (add), verdict: accepted and not
stored.** FR-009 names these as accepted without being stored. Added to `META_FIELDS` in T004 (not
`PARENT_COLUMNS`/`CHILD_COLUMNS`, which would additionally require entries in `columns.py`'s
`PublishedColumns.ENTRIES` per `test_columns.py::test_every_published_column_has_an_entry` — `ID`,
unlike the three reviewer columns, already resolves through
`GHFDBChildImportResource.ghfdb_id` (`column_name="ID"`), so double-declaring it as
"accepted-and-not-stored" would misstate what the code does; T005's named collection carries it
anyway, per the brief, since the OR in T005's assertion makes the redundancy harmless). `META_FIELDS`
is not consumed by `admin.py`'s `list_display_for`, so this addition carries no admin regression risk
matching Country/Region/Continent/Domain's.

**Consequence**: T002's test is deliberately one-directional (`resolved == set(header)`, not
`set(header) == set(PARENT_COLUMNS + CHILD_COLUMNS + META_FIELDS)`). The reverse direction would also
require `PARENT_COLUMNS`/`CHILD_COLUMNS`/`META_FIELDS` to drop `ID_parent`, `quality_parent`,
`quality_child`, `Quality_Code_Child` and `Quality_Score_Parent` — names the constants carry that the
template does not. `ID_parent` is required to stay by
`test_admin.py::test_site_values_are_not_restated_on_every_row`, which asserts
`headings & set(PARENT_COLUMNS) == {"ID_parent", "name", "lat_NS", "long_EW"}`; removing
`quality_parent` would flip `test_schema_coverage.py::test_parent_resource_declares_all_parent_columns`
from a `strict=True` xfail (documented against issue #122) to an unexpected pass, which is itself a
failure. Both are pre-existing tests outside this story's scope (constants.py and columns.py only),
so both names — and, for consistency and minimal diff, their siblings `quality_child`,
`Quality_Code_Child` and `Quality_Score_Parent` — are left exactly as they are. This story's claim is
narrower than literal set equality: every column the template carries is recognised (FR-004); it does
not claim every name the constants carry is one the template recognises.

**Revisit if**: issue #122 is resolved and the half-landed BUG-010 work is finished — at that point
`ID_parent`/`quality_parent`/`quality_child`/`Quality_Code_Child`/`Quality_Score_Parent`'s place in
these constants should be reconsidered as part of that work, not this one.

## D9 — US-1's first acceptance scenario is amended to match ADR 0003

**Decision**: acceptance scenario 1 of US-1 said every one of the template's seventy columns
resolves to "either a stored field or an explicitly accepted-and-ignored column". Two of them
resolve to neither, by design: `tc_pT_fuction` and `Ref_ISGN`, which ADR 0003 refuses rather than
maps. The scenario is amended to name all four outcomes a column can have, and scenario 2 now
states the consequence plainly — the template distributed today carries both misspellings, so a
file produced from it is refused on those two names until IHFC corrects the template.

**Why**: the contradiction was in the specification, not in ADR 0003 or in the implementation. The
ADR is explicit that both misspellings are "present in the currently distributed upload template",
that rejecting loudly is deliberately stricter than translating quietly, and that the revisit
condition is the template being corrected upstream. The specification sentence was written before
the ten disagreements had been enumerated against the real file, and it described an outcome the
recorded decision forbids. Amending the sentence I wrote is the correct repair; reopening a
decision Sam declined to reopen at the specification gate is not.

**Consequence**: until the published template is corrected, the portal imports no file produced
from it. That is the intended pressure, and it is a fact worth carrying to the merge gate rather
than discovering at first real use.

**Revisit if**: IHFC corrects the published template. ADR 0003's own revisit clause then applies —
the refusal narrows to a migration aid for files produced against older templates.

## D10 — the reconciliation test lives with the module it is about

**Decision**: the reconciliation and refusal tests were written to
`tests/test_ghfdb/test_resources/test_template_columns.py`, the path `plan.md` named. They test
`project/ghfdb/constants.py`, so they were moved to `tests/test_ghfdb/test_constants.py` and the
workbook fixture moved with them, from `tests/test_ghfdb/test_resources/conftest.py` up to
`tests/test_ghfdb/conftest.py`.

**Why**: constitution Article X requires the test tree to mirror the source tree, and the mechanical
structure check reads it that way — a test file under `test_resources/` is taken to be about a module
under `resources/`, and no `resources/template_columns.py` exists or should. The plan named a path
that no module backs. Moving the tests also returned `test_resources/conftest.py` to its committed
state, which is why the diff no longer modifies a pre-existing test file.

**Revisit if**: the header-validation surface moves out of `constants.py`.

**Guardrail triage**: the diff modifies one pre-existing test file,
`tests/test_ghfdb/conftest.py`, and the structural check flags it. Reviewed and approved: the change
is eighteen added lines declaring one new fixture, `official_upload_template_workbook`. No existing
fixture, assertion or test is altered, removed or weakened, and the suite it supports grew from 639
to 646 passing tests across the story.

## D11 — Removing the dataset-guessing fallback breaks 37 pre-existing tests, left unfixed

**Ambiguous because** T008 requires removing
`kwargs.get("fairdm_dataset") or FairDataset.all_objects.first()` from both resources'
`before_import`, and every pre-existing test in `test_parent_import.py` and `test_child_import.py`
that calls `import_data()` without passing `fairdm_dataset=` was — unknowingly — relying on exactly
that fallback: a `dataset` fixture exists in the database, `all_objects.first()` silently finds it,
and the test passes without ever naming its target. Removing the fallback (FR-002, T007, T008) turns
every one of those calls into the located `ValueError` T008 adds. Confirmed by running
`tests/test_ghfdb/test_resources/test_parent_import.py tests/test_ghfdb/test_resources/test_child_import.py`
after the change: 37 pre-existing tests fail, all with the same cause.

**Chosen**: the fallback is removed, per T008, and the 37 tests are left exactly as they are —
neither their assertions nor their call sites are touched. `craft-tdd`'s prohibition is explicit:
never modify or delete a test this story did not author, and a pre-existing test that must change is
reported, not silently repaired. Reported in this run's `concerns`, with the full test list and the
one-line fix (`fairdm_dataset=dataset`, the pattern `test_roundtrip.py` already uses at four call
sites), for Forge to apply or dispatch.

**Defensible because** the alternative — editing 37 tests I did not author, across two files, to
keep the run's own suite green — is precisely the shortcut the prohibition exists to prevent. The
fix is mechanical and the resulting call sites would be indistinguishable from ones written with
intent, which is exactly why an Implementer must not be the one who makes that judgement silently.
This mirrors D9's approach: a real, foreseen consequence of a correct change, accepted and recorded
rather than patched around.

**Consequence accepted**: `poetry run pytest tests/test_ghfdb/` (and the full repo verify) reports
these 37 as newly failing until the call sites are updated. Every other test in the two files —
including the ones this story added for T007, T009, T011 and T012 — passes on its own narrow scope.

**Revisit if**: never — this is a one-time migration. Once the 37 call sites carry `fairdm_dataset=`,
the fallback's removal has no further pre-existing-test cost.

## D12 — `importers.py` takes either a raw file or an already-parsed dataset; the admin path is not
made functional

**Ambiguous because** T013 asks for one callable "taking a file and a dataset," and for "the admin
import path" to call it rather than duplicate its sequence. `spec.md`'s Assumptions are explicit that
this feature has "nothing... a person clicking anything" — the upload page belongs to a later
roadmap item (R6/R7) — yet `GHFDBParentAdmin` and `GHFDBChildAdmin` already expose a working Django
admin import wizard today, built on `django-import-export`'s `ImportExportMixin`. That wizard commits
through `process_dataset(dataset, form, request, **kwargs)`, which by the time it runs already holds
a parsed `tablib.Dataset` — never the raw uploaded bytes — and neither admin class has ever had a way
to name a target `Dataset`; both silently relied on the same `.first()` fallback T008 removes.

**Chosen**: `import_ghfdb_template(file, dataset)` accepts either raw file bytes/a file-like object
or an already-parsed `tablib.Dataset`, so both a code caller (FR-001, holding a real file) and
`GHFDBParentAdmin.process_dataset` (holding an already-parsed one) reach the same function without
either re-serialising a dataset back to bytes or re-reading a spent upload stream.
`GHFDBParentAdmin.process_dataset` is overridden to call it — the one admin path this story
touches, since it is the site-and-parent import US-2 owns; `GHFDBChildAdmin`'s separate wizard is
untouched. Neither override adds a way to name the target dataset: with none available, the call
always raises T008's located error, so the admin import routes remain unable to complete a real
import until a dataset-selection surface exists.

**Defensible because** building that surface is explicitly out of this feature's scope (spec.md
Assumptions: "the upload page... belong[s] to R6's other half and to R7"), and it was never
functional in the sense of writing to a caller-chosen dataset — it always wrote to whichever dataset
happened to be first. Failing loudly now is strictly better than the silent wrong-dataset write it
replaces, and FR-002 requires exactly that refusal regardless of caller.

**Consequence accepted**: the Django admin's GHFDB import actions raise on every use until a
dataset-selection mechanism is added; there is no regression in what a curator could reliably do
through them, since neither route ever safely chose the right dataset before.

**Revisit if**: R6/R7 adds a dataset-selection surface to either admin path — at that point it
supplies `dataset=` to `import_ghfdb_template` and the route becomes usable again.

## D13 — TC01: the 37 call sites D11 left unfixed now carry `fairdm_dataset=dataset`

**Ambiguous because** D11 recorded 37 pre-existing tests across `test_parent_import.py` and
`test_child_import.py` failing because they called `import_data()` without naming a dataset, and
explicitly declined to fix them in that story — a pre-existing test that must change is reported,
not silently repaired by the story that broke it. This follow-on task is that sanctioned repair,
scoped to exactly the fix D11 already named: add `fairdm_dataset=dataset` to each call site, and
nothing else.

**Chosen**: every `import_data()` call in both modules that omitted `fairdm_dataset=` now passes
`fairdm_dataset=dataset` — the `dataset` fixture every one of the 37 tests already receives,
matching the pattern `test_roundtrip.py` already used at four call sites. In
`test_child_import.py`, most call sites are covered by fixing the module's own `import_parents()`
helper once, since it already takes `dataset` as a parameter and every caller passes it through.
No assertion, fixture, row, expected value, class or name in either module changed — confirmed by
diff review before each commit, and by running the narrowest scope after each edit.

**Defensible because** this is exactly the one-line, evidence-backed fix D11 already named as the
correct resolution, done as its own sanctioned change rather than folded into the story that
removed the fallback — the separation D11 argued for.

**Consequence accepted**: `poetry run pytest tests/test_ghfdb/test_resources/test_parent_import.py
tests/test_ghfdb/test_resources/test_child_import.py` reports 54 passed, 5 xfailed (the same 5
pre-existing, unrelated xfails from BUG-006/#122) — the 37 tests D11 left failing are green, and
nothing else in either module moved.

**Revisit if**: never — this was the one-time migration D11 already scoped.

## D14 — US-3 needed no production change, so each of its tests was probed before being accepted

**Ambiguous because** every acceptance criterion in US-3 — one interval per determination, gradient
and conductivity and correction and probe values kept per determination, `relevant_child` mapped to
exactly the contributing children, every created object attached to the caller's dataset — already
held in `GHFDBChildImportResource` at the moment the story started. A test that passes the first
time it is run proves nothing on its own: it may be asserting something the code cannot fail.

**Chosen**: the story lands as tests only, with no edit to `project/ghfdb/resources/child.py`, and
each test earns its place by a probe rather than by passing. For each one the specific mechanism it
claims to cover was temporarily broken — the interval reused across rows, the gradient reused,
`is_relevant` hard-coded, the conductivity's dataset assignment dropped — the test was watched
failing for that reason, the file was restored, and the restore was confirmed byte-clean against a
pre-edit copy before the commit. The probe transcripts are in `progress.md` under T015, T017, T019
and T020.

**Defensible because** the alternative — rewriting working code so the story has a diff — would
trade a correct implementation for a risk, and the alternative to probing is a suite that grows
four tests nobody has evidence are load-bearing.

**Consequence accepted**: the guardrail that watches for changes to pre-existing tests flags this
story, because `test_child_import.py` existed before it. The change is append-only: 211 added lines,
zero removed, four new classes at the end of the module, no assertion or fixture above them touched.
Triaged and approved on that evidence.

**Revisit if**: a later story changes `child.py` in a way these four tests do not catch — that would
mean the probes chose the wrong mechanism to break.

## D15 — `clean_model_instances = True` needs `validate_instance()` to exclude three fields, or it refuses every row

**Ambiguous because** T022 asks for `clean_model_instances = True` on both resources' `Meta`, on the
strength of DR-002's claim that this is what makes `result.has_validation_errors()` populate at all.
Turning it on exactly as described broke every previously-passing test in
`tests/test_ghfdb/test_importers.py` and both `test_resources` import modules — not on anything the
row data got wrong, but on `sample`, `dataset` and `name`, all required by the `Measurement` base
class (`fairdm.core.measurement.models`) and all still unset at the point `full_clean()` runs.

**Confirmed in the code**: `import_row()` calls `validate_instance()` — which is where
`full_clean()` runs when `clean_model_instances` is true — before `save_instance()`, and
`save_instance()` is what calls `before_save_instance()`. Both resources' `before_save_instance()`
is where `instance.sample` (the site, or the depth interval) and `instance.dataset` are set; neither
resource ever sets `instance.name` on the measurement itself (the *site's* name is a separate field,
already stored on `HeatFlowSite`). `full_clean()` therefore always saw `sample`, `dataset` and `name`
as blank, on every row of every file, refusing files that had nothing wrong with them at all.

**Chosen**: both resources override `validate_instance()` to call `full_clean(exclude={...,
"sample", "dataset", "name"})` — the base implementation's own logic, with those three fields added
to the exclusion set alongside the fields `import_instance()` already flagged. `before_save_instance`
still sets all three, moments later, before the row is saved; the DB's own NOT NULL constraint is
the backstop if either resource ever fails to. `has_errors()` already rolls back on a row-level
exception regardless of `rollback_on_validation_errors` (`import_export/resources.py:851-855`), so
that backstop still refuses the file — it would simply report a database-level message instead of a
located, translated one.

**Defensible because** `sample`, `dataset` and `name` are resource-internal linkage, not columns the
uploaded file supplies — FR-011's fourth fault type is about a *spreadsheet cell* left empty that
maps to a required model field (`q`, `qc`, and siblings via `QuantityWidget`), not about the plumbing
that attaches a row to its site and dataset. Restructuring both resources so every hook that
populates a relation runs before `import_instance()`/`validate_instance()` would fix the same problem
at a structural level, but it is a far larger, riskier diff than this story's scope (`Meta` and the
entry point, per `plan.md`), for the same practical result on every case this story's tests cover.

**Consequence accepted**: a genuine future bug that left `sample`, `dataset` or `name` unset on save
would still surface as an unlocated `IntegrityError`-shaped row error rather than a located,
translated `full_clean()` message. It would still refuse the file — `has_errors()` does not depend on
the flag — just with a worse message than the fields this story's fault type actually targets get.

**Revisit if**: a later story moves relation-population into `after_init_instance()` (or another hook
that runs before `validate_instance()`) for both resources — at that point the exclusion is no longer
needed and should be removed along with it.
