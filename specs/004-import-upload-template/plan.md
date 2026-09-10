# Implementation Plan: Import a completed upload template into a dataset

**Branch**: `004-import-upload-template` | **Date**: 2026-09-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/004-import-upload-template/spec.md`

## Summary

Two import resources already exist and are wired into the Django admin:
`GHFDBParentImportResource` (`project/ghfdb/resources/parent.py`) and `GHFDBChildImportResource`
(`project/ghfdb/resources/child.py`), both `django-import-export` `ModelResource` subclasses reading
a spreadsheet whose headers sit on row 6. The feature does not build a reader from nothing. It makes
the existing pair read the real published template, holds them to the refusal guarantee they only
claim to have, and gives them a callable entry point that takes a dataset rather than finding one.

The work divides along the seams already in the code:

| Story | Where it lands |
|---|---|
| US-1 official template is what the reader reads | `constants.py`, `columns.py`, `tests/fixtures/` |
| US-2 sites and parent values, into a named dataset | `resources/parent.py`, a new callable entry point |
| US-3 child determinations beneath their sites | `resources/child.py`, `resources/widgets.py` |
| US-4 refused whole, every fault located (#190) | both resources' `Meta`, the entry point |
| US-5 the portal's vocabularies decide | `resources/widgets.py` (`ConceptWidget`, `MultiConceptWidget`) |
| US-6 repeat import updates in place | `import_id_fields` on both resources |

## Technical Context

**Language/Version**: Python 3.13 (single target, per the repository's CI)

**Primary Dependencies**: Django 5.2, `django-import-export` 4.3.9, FairDM, `research_vocabs`
(`ConceptField`), `openpyxl` through `import-export`'s XLSX format

**Storage**: PostgreSQL with PostGIS. Sites carry a `Point`; datasets come from `fairdm.core.models`

**Testing**: pytest with pytest-django and factory-boy, tests mirroring the source tree under
`tests/test_ghfdb/test_resources/`

**Target Platform**: the deployed portal, Linux server

**Project Type**: single Django project

**Performance Goals**: none stated. The published template carries 508 data rows, so a single import
is small. No streaming or chunking requirement follows from the spec

**Constraints**: the import writes nothing unless the whole file is acceptable; every fault is
located by row and column

**Scale/Scope**: 70 template columns, two resources, six stories

## Constitution Check

| Principle | Bearing on this feature |
|---|---|
| II. GHFDB Schema Fidelity | Column names come from the published template and are preserved exactly. US-1 is this principle applied to input. ADR 0002 and ADR 0003 already settle the misspelling question: a misspelled published name is corrected internally and rejected on input |
| III. FairDM-First | The dataset is a FairDM `Dataset`; nothing here reimplements dataset ownership |
| VI. Test-First (non-negotiable) | Every story is written test first. US-4 additionally requires the guard test proven against the reinstated defect |
| V. Internationalisation | Fault messages are user-facing strings and go through `gettext_lazy` |
| IX. Simplicity | The entry point is one function. No import framework, no plugin layer, no configuration surface the spec does not ask for |
| VII. Documentation | `docs/guides/importing-data.md` describes importing and is updated in the same pull request |

No violation requiring an entry in Complexity Tracking.

## Project Structure

### Documentation (this feature)

```
specs/004-import-upload-template/
├── spec.md
├── decisions.md
├── plan.md
├── tasks.md
└── progress.md
```

### Source Code (repository root)

```
project/ghfdb/
├── constants.py          # PARENT_COLUMNS, CHILD_COLUMNS, META_FIELDS  (US-1)
├── columns.py            # column metadata and lookups                 (US-1)
├── resources/
│   ├── parent.py         # GHFDBParentImportResource                   (US-2, US-4, US-6)
│   ├── child.py          # GHFDBChildImportResource                    (US-3, US-4, US-6)
│   └── widgets.py        # ConceptWidget, MultiConceptWidget, others    (US-5)
└── importers.py          # NEW: the callable entry point               (US-2)

tests/
├── fixtures/             # the official template, copied unmodified    (US-1)
└── test_ghfdb/test_resources/
    ├── test_parent_import.py
    ├── test_child_import.py
    ├── test_template_columns.py   # NEW                                (US-1)
    └── test_refusal.py            # NEW                                (US-4)
```

**Structure Decision**: the existing single-project layout stands. One new module,
`project/ghfdb/importers.py`, holds the callable entry point, because the thing the spec asks for —
one file into one named dataset, refused whole — is an operation over both resources and belongs to
neither of them.

## Approach, story by story

### US-1 — The official template is what the reader reads

Copy `docs/constitution/references/data_upload_template.xlsx` into `tests/fixtures/` unmodified and
make it the fixture the reader is tested against. Read its header row (row 6, the `Short Name` row)
and reconcile it against `PARENT_COLUMNS + CHILD_COLUMNS + META_FIELDS`. Write the reconciliation as
a test that reads the template at run time and asserts set equality against the constants, so the
ten known disagreements fail loudly and a future revision of the template does the same.

Where a constant and the template disagree, the template wins, unless ADR 0003 already names the
template's spelling as one of the corrected misspellings, in which case the existing correction
stands and the test records the exception explicitly rather than silently.

Accepted-and-not-stored columns are declared in one place rather than being absent from the mapping,
so "unmatched" and "deliberately ignored" stop looking the same.

### US-2 — Sites and parent values, into a named dataset

`GHFDBParentImportResource.before_import` currently resolves the dataset as
`kwargs.get("fairdm_dataset") or FairDataset.all_objects.first()`. The fallback is the behaviour
FR-002 forbids: with no dataset passed it silently fills whichever dataset happens to be first.
Remove the fallback and raise instead.

Add `project/ghfdb/importers.py` with one public callable taking a file and a dataset, which runs
both resources in the right order inside one transaction and returns the outcome. The admin path
keeps working by calling the same entry point.

### US-3 — Child determinations beneath their sites

`RelatedModelWidget` and its subclasses (`IntervalWidget`, `GradientWidget`, `ConductivityWidget`,
`ParentWidget`) already build the child-side objects. The work is to prove each one against the real
template's columns, attach every child to the dataset rather than to whatever the parent resolved,
and make `relevant_child` reflect the children that actually fed the parent value.

### US-4 — Refused whole, every fault located

`rollback_on_validation_errors = True` sits in both resources' `Meta`, where
`django-import-export` 4.3.9 never reads it: it is a keyword argument to `import_data()`, and
`import_export/options.py` declares no such option (#190). The entry point passes it as the argument
it is, and a test reinstates the `Meta` form to prove the guard fails when the enforcement is
removed.

Collect faults for the whole file rather than raising on the first. `import-export`'s result object
already carries per-row errors, so this is a matter of running the whole pass in dry-run, gathering
`result.row_errors()`, and only committing when that is empty.

**Row errors already roll back; validation errors do not.** `resources.py:851-855` rolls back on
`result.has_errors()` regardless of the flag, so the flag's only effect is on
`result.has_validation_errors()` — and that is populated from `Model.full_clean()` only when
`Meta.clean_model_instances` is `True`, which defaults to `False` (`options.py:88`) and is set
nowhere in this repository. FR-011's fourth fault type, an empty mandatory model field, therefore has
no path to a located fault today: it either writes, or surfaces as a raw `IntegrityError` naming no
column and passing through no translation. Both resources get `clean_model_instances = True`, and a
test covers the empty-mandatory-field case specifically.

### US-5 — The portal's vocabularies decide

There are **three** places a vocabulary value is interpreted, not two, and the third is where the
rule currently fails.

`ConceptWidget.clean` and `MultiConceptWidget.clean` both resolve against the portal's own concepts
and raise when they cannot. That is correct today. But every many-valued vocabulary column reaches
`MultiConceptWidget.clean` through `RelatedModelWidget.set_m2m_relations`
(`resources/widgets.py:283-295`), which wraps the call in `except (ValueError, ValidationError):
pass`. The exception never reaches `import_row`, so the row is not refused and the relation is left
quietly unset. Thirteen of the template's controlled-vocabulary columns take that path:
`explo_purpose`, `geo_lithology`, `geo_stratigraphy`, `T_method_top`, `T_method_bottom`,
`T_corr_top`, `T_corr_bottom`, `tc_source`, `tc_location`, `tc_method`, `tc_saturation`,
`tc_pT_conditions`, `tc_pT_function` and `tc_strategy`.

The swallow has to go, or narrow to something that is genuinely not a fault. `set_m2m_relations`
runs from `after_save_instance`, after the row is saved inside the transaction, so an unrecognised
concept must be recorded as a row error the resource checks before committing rather than raised
into the void.

Nothing anywhere may read the template's `controlled vocabulary` sheet, and a test asserts that the
sheet is not consulted, using a value that sheet lists and the portal does not hold. **That test
uses one of the thirteen columns above**, not a single-valued one, because a test written against
`environment` passes while the defect ships.

### US-6 — Repeat import updates in place

Both resources declare `import_id_fields`. Parent keys on `ID_parent` with a documented fallback to
the site's coordinates. Confirm the fallback holds for template rows, which carry no `ID_parent`, so
a second import of the same file matches rather than inserting.

**The child natural key contains the values a correction is most likely to change.**
`child.py:361-370` builds it from `lat_NS`, `long_EW`, `q_top`, `q_bottom` and
`publication_reference`. A resubmitted file that corrects a depth interval no longer matches its own
earlier row, so `get_or_init_instance` falls through and writes a second determination under the
same site. The changed-value test therefore changes `q_top` or `q_bottom` specifically. Whether the
right answer is a narrower key or something else is a decision for the story, recorded in
`decisions.md`.

## Sequencing

US-1 first: every other story's tests read the template, so the fixture and the column reconciliation
are the foundation. Then US-2, US-3 in order, since child rows attach to sites the parent pass
creates. US-4 next, once there is something real to refuse. US-5 and US-6 are independent of each
other and land last.

## Risks

- **The ten column disagreements may not all be renames.** If one is a column the model has no home
  for, US-1 turns into a decision rather than a rename, and that decision goes in `decisions.md`.
- **The parent/child split across one row.** Each template row carries both parent and child columns,
  so a single-file import is two passes over the same rows. The transaction has to span both.
- **`all_objects` on the dataset lookup** exists to reach private datasets. Removing the fallback
  must not change that: the caller's named dataset is still resolved through the manager that sees
  private ones.
