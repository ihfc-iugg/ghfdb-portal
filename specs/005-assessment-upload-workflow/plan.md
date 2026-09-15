# Implementation Plan: Upload a completed assessment template through the portal

**Branch**: `005-assessment-upload-workflow` | **Date**: 2026-09-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/005-assessment-upload-workflow/spec.md`

## Summary

Build the pages the data assessment team uploads a completed GHFDB template through, on top of the
reader FS-004 delivered. An assessment is described first, the file is then checked without writing,
failures are rendered in the template's own column names, and a confirmation writes the data and
sets the dataset's visibility from the uploader's role. An assessor's upload waits in a queue for a
curator's decision.

The work concentrates in `project/review/`, which today holds a partial version of the assessment
record and no tests. Three things change outside it: a checking parameter on the reader in
`project/ghfdb/importers.py`, the glossary in `CONTEXT.md`, and the roadmap.

## Technical Context

**Language/Version**: Python 3.13, Django 5.2

**Primary Dependencies**: FairDM (application shell, views, contributors, datasets),
django-literature (publication catalogue), django-import-export (the reader's engine),
django-guardian (object permissions), flex-menu (site navigation), django-select2

**Storage**: PostgreSQL. Submitted files on the configured media storage, referenced from the
assessment record.

**Testing**: pytest, pytest-django, factory-boy. Test tree mirrors `project/` under `tests/`.

**Target Platform**: Linux server, rendered server-side by Django templates

**Project Type**: Django web application

**Performance Goals**: none specific. An upload is one user action on a file of a few hundred rows.

**Constraints**: a file is never partially written. The check and the write must agree, and the
write must be safe to trigger twice.

**Scale/Scope**: a team of roughly ten people, one publication at a time.

## Constitution Check

*GATE: passed before Phase 0 research, re-checked after the design below.*

| Article | Bearing on this feature | Verdict |
|---|---|---|
| I. FAIR-First Scientific Data | The submitted file is retained against the assessment, so every dataset traces to its source spreadsheet. Assessors are credited as contributors. | Advances it |
| II. GHFDB Schema Fidelity | No column mapping, vocabulary resolution or schema behaviour changes. The reader is called, not modified, apart from a checking parameter. | No impact |
| III. FairDM-First Integration | Pages are built on the framework's own view classes, plugin registration and navigation. No parallel UI stack. | Conforms |
| IV. Open Science, Provenance & Review Governance | The article the feature serves: the decision, its maker and its date are recorded, and nothing an assessor uploads is public without a curator. | Advances it |
| V. Internationalisation | Every user-facing string uses `gettext_lazy`. Every model field carries `verbose_name` and `help_text`. | Conforms, enforced per task |
| VI. Test-First (non-negotiable) | The application has no tests. Each task writes its failing test first, and the test tree is established in the foundational phase. | Conforms |
| VII. Documentation Critical | New pages and the two roles are documented in `docs/` in this pull request. `CONTEXT.md` gains the role vocabulary. | Conforms, own tasks |
| VIII. Spec-Driven Workflow | This plan follows an approved specification. | Conforms |
| IX. Simplicity & Maintainability | The largest simplicity decision is refusing to add a notification framework for one use. Recorded in `decisions.md`. | Conforms |
| X. WHDB Mission | The assessment team is the portal's primary internal user, and this takes the Django admin out of their path. | Advances it |

No violations to justify.

## Design

### The record

`Review` grows the fields the workflow needs and keeps everything it has. The publication stays a
one-to-one relation, as the specification and `CONTEXT.md` both require. Full field list and state
vocabulary: [data-model.md](./data-model.md).

The state vocabulary is the spine of the feature. Every page is reachable only from certain states
and every transition is one of a small closed set, so the states live on the model and the views ask
the model rather than testing field combinations themselves.

### The checking mode

`import_ghfdb_template(file, dataset)` gains a `check_only` parameter, defaulting to `False`. When
true, both passes run with `dry_run=True` and the transaction is rolled back unconditionally. The
existing callers are unaffected.

The two `Result` objects already carry what the report needs. A thin reading layer turns them into
the counts FR-009 asks for and the per-row failures FR-012 asks for, with the template's own column
headings substituted from `project/ghfdb/columns.py`. That layer belongs in `project/ghfdb/`, beside
the reader whose output it reads, rather than in the view that renders it.

### The pages

Seven views in `project/review/views.py`, all on the framework's own base classes:

| View | Route | Access |
|---|---|---|
| Assessment list | `/assessments/` | either role |
| Start an assessment | `/assessments/new/` | either role |
| Upload a file | `/assessments/<pk>/upload/` | the assessment's uploader, or any curator |
| Check report | same route, rendered from the check | same |
| Confirm | `/assessments/<pk>/confirm/` | same, POST only |
| Decision queue | `/assessments/queue/` | curators only |
| Decide | `/assessments/<pk>/decide/` | curators only, POST only |

The check report and the upload form share one template with three states, empty, failed and
checked, which is how `fairdm/contrib/import_export/templates/import_export/import.html` already
works.

### Roles and access

Two Django groups, created by a data migration rather than a fixture, so they exist in every
environment without a load step and without pinning permission primary keys. A small predicate
module holds `is_data_assessor` and `is_data_curator`, and every view, navigation check and template
condition calls those two functions rather than testing group names inline. That is what stops the
case-sensitivity defect the current code carries from recurring.

The framework's `Person.is_data_admin` is fixed to a group named "Data Administrators" and gates its
own import and publication views. This feature does not rename that group. The portal's Data Curator
group is created alongside it and the portal's pages check the portal's own predicate. Whether the
two should be reconciled upstream is recorded as a decision rather than resolved here.

### Confirmation safety

Confirmation re-runs the check against the stored file rather than trusting the report the user saw,
then writes in the same transaction. The assessment's state is the idempotency key: a confirmation
arriving for an assessment already written is a no-op that redirects to the result. One mechanism
covers both the double submission in FR-024 and the stale report in the edge cases.

### Notification

The navigation entry carries the number of assessments waiting on a decision, visible to curators,
and the queue lists them. No notification framework is added. Reasoning and rejected alternatives:
[decisions.md](./decisions.md).

## Project Structure

### Documentation (this feature)

```text
specs/005-assessment-upload-workflow/
├── plan.md
├── spec.md
├── research.md
├── data-model.md
├── decisions.md
├── progress.md
└── tasks.md
```

### Source Code (repository root)

```text
project/
├── review/
│   ├── models.py          # Review grows files, uploader, decision, states
│   ├── states.py          # the state vocabulary and its transitions
│   ├── permissions.py     # is_data_assessor / is_data_curator predicates
│   ├── forms.py           # the description form, the upload form
│   ├── views.py           # the seven views above
│   ├── menus.py           # the navigation entry, currently commented out
│   ├── urls.py
│   ├── migrations/
│   └── templates/review/  # list, description, upload and report, queue, decision
└── ghfdb/
    ├── importers.py       # check_only parameter
    └── report.py          # Result objects to counts and per-row failures

tests/
└── test_review/           # new: mirrors project/review/, with factories
    ├── conftest.py
    ├── factories.py
    ├── test_models.py
    ├── test_permissions.py
    ├── test_views/
    └── test_workflow.py   # the end-to-end path per story

docs/
└── guides/                # the team's own page for this workflow
```

**Structure Decision**: the feature lives in the existing `review` application, which `CONTEXT.md`
already defines as owning the process by which a publication becomes a dataset. The reporting layer
sits in `ghfdb` because it reads that application's output and speaks the spreadsheet's column
names, and `CONTEXT.md`'s rule is that the spreadsheet's language stays on the `ghfdb` side of the
boundary.

## Complexity Tracking

No constitution violations require justification.
