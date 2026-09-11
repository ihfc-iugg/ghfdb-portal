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
