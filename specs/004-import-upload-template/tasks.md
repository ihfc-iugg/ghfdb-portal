# Tasks: Import a completed upload template into a dataset

**Branch**: `004-import-upload-template` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

Every task is written test first, per constitution Article VI. A task is done when its test fails for
the stated reason before the change and passes after, and the class it belongs to is green.

## Foundational

- **T001** Copy `docs/constitution/references/data_upload_template.xlsx` into `tests/fixtures/` under
  a name that says what it is, unmodified, and add a fixture that opens it. No other change.
- **T002** Add `tests/test_ghfdb/test_resources/test_template_columns.py` with a test that reads the
  fixture's header row and asserts set equality against
  `PARENT_COLUMNS + CHILD_COLUMNS + META_FIELDS`. Expected to fail on ten names. Record the ten in
  the test's failure message rather than hard-coding them.

## US-1 — The official template is what the reader reads (#200)

- **T003** For each of the ten disagreements, decide rename or exception: the template's spelling
  wins unless ADR 0003 already names it as a corrected misspelling. Write the decision into
  `decisions.md` as one entry with the ten listed.
- **T004** Apply the renames to `constants.py` and any lookup in `columns.py` that repeats them.
  T002 goes green.
- **T005** Declare the accepted-and-not-stored columns (the reviewer columns and `ID`) in one named
  collection, and assert in `test_template_columns.py` that every template column is either mapped
  by a resource field or in that collection.
- **T006** Add a test that a file whose header row is not the template's is refused, naming the
  header, and that nothing is written.

## US-2 — Sites and parent values, into a named dataset (#201)

- **T007** Test: importing with no dataset named raises rather than choosing one. Fails today,
  because `before_import` falls back to `FairDataset.all_objects.first()`.
- **T008** Remove the fallback in `parent.py` and `child.py`; raise a located error instead. T007
  goes green. The named dataset is still resolved through the manager that sees private datasets.
- **T009** Test: a file of rows across two coordinate pairs produces two sites in the named dataset,
  each with the parent value its P-columns describe.
- **T010** Make T009 pass.
- **T011** Test and confirm: geography columns are stored as supplied, not recomputed.
- **T012** Test and confirm: the reviewer columns and `ID` are accepted and not stored, and their
  presence is not an error.
- **T013** Add `project/ghfdb/importers.py` with the public callable taking a file and a dataset.
  The admin path calls it rather than duplicating it.

## US-3 — Child determinations beneath their sites (#202)

- **T014** Test: rows describing two determinations at one coordinate pair produce two
  determinations beneath one site, each with its own depth interval.
- **T015** Make T014 pass.
- **T016** Test: gradient, conductivity, correction and probe values land against their own
  determination, using real template column names.
- **T017** Make T016 pass.
- **T018** Test: `relevant_child` names exactly the children that fed the parent value, and no
  others.
- **T019** Make T018 pass.
- **T020** Confirm every child object is attached to the named dataset rather than to whatever the
  parent pass resolved.

## US-4 — Refused whole, every fault located (#203, closes #190)

- **T021** Test: with the rollback declared as it is today, a file with a late fault leaves rows
  written. This is the reproduction of #190 and must fail before the fix.
- **T022** Pass `rollback_on_validation_errors` as the `import_data()` argument it is, from the entry
  point, and remove the declaration from both resources' `Meta`. Set `clean_model_instances = True`
  on both resources' `Meta` in the same change: without it `result.has_validation_errors()` is never
  populated, so the flag being passed correctly still enforces nothing beyond what row errors already
  roll back. T021 goes green.
- **T023** Test: reinstating the `Meta` form makes the suite fail, so the guarantee is guarded rather
  than assumed.
- **T024** Test: a file with faults on two widely separated rows reports both, each naming its row
  and column.
- **T025** Run the whole pass in dry-run, gather every row error, and commit only when there are
  none. T024 goes green.
- **T026** Test: a clean file imports with nothing reported and every row landed.
- **T026a** Test: a row with an empty mandatory model field produces a fault naming its row and
  column, in a translated message, and refuses the whole file. This is FR-011's fourth fault type,
  and it is the one with no enforcement path before T022 adds `clean_model_instances`.

## US-5 — The portal's vocabularies decide (#204)

- **T027** Test: a value the portal holds no concept for refuses the file, naming row, column and
  value.
- **T028** Make T027 pass in `ConceptWidget.clean` and `MultiConceptWidget.clean`.
- **T028a** Remove or narrow the `except (ValueError, ValidationError): pass` in
  `RelatedModelWidget.set_m2m_relations` (`resources/widgets.py:294-295`). Every many-valued
  vocabulary column reaches `MultiConceptWidget.clean` through it, so an unrecognised concept in any
  of thirteen columns is currently discarded and the relation left unset instead of refusing the
  file. `set_m2m_relations` runs after the row is saved, inside the transaction, so the fault has to
  be recorded where the resource checks it before committing rather than raised into nothing.
- **T028b** Test T027's rule again using one of the thirteen many-valued columns — `geo_lithology`,
  `tc_method` or a sibling — never `environment` or another single-valued column. A test written
  against a single-valued column passes while the defect ships.
- **T029** Test: a value the template's own vocabulary sheet lists, which the portal does not hold,
  is still refused. This is the rule stated backwards on purpose, and it is the one most likely to be
  implemented the wrong way round.
- **T030** Test: a value the portal holds, which the sheet does not list, is accepted.
- **T031** Assert that nothing in the import path opens the template's `controlled vocabulary` sheet.

## US-6 — Repeat import updates in place (#205)

- **T032** Test: importing the same file twice leaves site and determination counts unchanged.
- **T033** Make T032 pass. Template rows carry no `ID_parent`, so confirm the coordinate fallback in
  `import_id_fields` matches rather than inserting.
- **T034** Test: a file identical except for a changed `q_top` or `q_bottom` updates the
  determination in place and duplicates nothing. The changed field is named deliberately: the child
  natural key is built from `lat_NS`, `long_EW`, `q_top`, `q_bottom` and `publication_reference`
  (`child.py:361-370`), so a depth-interval correction — the most plausible real one — currently
  fails to match its own earlier row and writes a second determination. A test that changed `qc`
  instead would pass over the top of that.
- **T035** Make T034 pass. Whether the answer is a narrower natural key or something else is this
  story's decision to take, and it goes in `decisions.md` with its reasoning.

## Documentation

- **T036** Update `docs/guides/importing-data.md` for the callable entry point, the refusal rule and
  the vocabulary rule, and run its examples against the branch.

## Dependencies

T001 and T002 precede everything. US-2 precedes US-3, because child rows attach to sites the parent
pass creates. US-4 follows US-3, so there is something real to refuse. US-5 and US-6 are independent
of each other.
