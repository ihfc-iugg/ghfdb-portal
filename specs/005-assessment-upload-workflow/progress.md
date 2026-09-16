# Progress — 005 assessment upload workflow

## 2026-09-15 — Spec gate: approved

Approved by Sam in session, on the epic (#209) plus its six story sub-issues (#210–#215) and
`spec.md` on this branch. Draft pull request #216 open.

Approved as specified, with no changes requested. The scope recorded at the gate:

- R6's remaining half together with the role, the private-until-approved rule and the approval
  queue from R7. R7 narrows to contribution from outside the assessment team.
- R7's deliverable placing team members outside the gate is superseded: a Data Curator's upload
  does not wait, a Data Assessor's does.
- CONTEXT.md adopts Data Assessor and Data Curator, retiring "Reviewer" and "data administrator".

Carried forward as a known risk rather than a blocker: the distributed upload template still
carries the two column misspellings ADR 0003 refuses, so real files cannot pass these pages until
the template is corrected upstream. That correction is outside this feature.

Next: plan, task graph, design review.

## 2026-09-16 — US-1 complete (T010b, T011, T012, T014, T013)

T010b first, closing the documentation gate US0 left red: the nine public names it introduced
across `review.states`, `review.permissions`, `review.models` and `ghfdb.report` are now quoted in
`docs/data_models/ghfdb-erd.md` and `docs/guides/importing-data.md` (the latter also gains a section
on `check_only` and the checking report), and the two stale-page findings on
`docs/development/testing-standards.md` and `docs/ghfdb_fields.md` are resolved.

Then the list itself: `ReviewListView` (`FairDMListView` + `UserPassesTestMixin`), its item
template, the route and the navigation entry, in that order except T014's route registration landed
inside T011's commit and T013 followed T014 rather than preceding it — both forced by dependencies
tasks.md doesn't surface; recorded as D15.

Two things found along the way, both recorded as decisions rather than worked around silently:
`FairDMListView`'s auto-generated `FilterSet` can't handle `Review`'s `PartialDateField`s (D14, fixed
by pinning `filterset_fields = []`), and this project's shared page chrome raises for any
authenticated request once rendering reaches the sidebar — reproduces on the pre-existing
`/datasets/` page too, so it predates this story (D16). Flagged for separate triage; the story's own
tests are scoped around it rather than depending on it.

Full suite: 827 passed, 1 skipped, 13 xfailed. `forge verify --steps docs --base 1caed37` clean.
`manage.py check` and `makemigrations review --check` both clean.

Next: US-2, the description form.

## 2026-09-16 — US-2 complete (T015, T016, T018, T017, T019)

`ReviewDescriptionForm` (T015): publication, assessors and dates, with an optional title field that
belongs to the dataset rather than the model. Assessors are drawn from `Person.objects.real()`,
so a ghost profile with no account validates; end-before-start is refused naming both dates,
compared as `PartialDate` rather than as strings (the model's own equivalent check lives in
`save()`, which form validation never reaches).

T016 made `literature` optional and added `bibliography_file`: a CSL-JSON file read with the
stdlib `json` module creates the `LiteratureItem` inline during `clean()`. D18 records why this
accepts CSL-JSON specifically rather than the BibTeX/RIS/EndNote `django-literature`'s own import
page supports — that page's parsing happens client-side, in a bundled JS library this repository
doesn't own, and no server-side parser is an available dependency here.

T018 added the duplicate check ahead of Django's own `validate_unique()`, naming the existing
assessment's dataset in the refusal rather than the framework's generic message.

T017 built `ReviewCreateView`: writes the `Review` in its default `DESCRIBED` state, creates a
`Dataset` left at the framework's private defaults (nothing sets `visibility` or `published`),
grants the uploader — never the assessor list — object permissions via `assign_all_model_perms`
(D20, correcting the retired view's grant of the same helper to every reviewer — see `git show
78c12d1`), and credits each assessor as a `DataCollector` contributor (D19, replacing the retired
view's `DataCurator` credit, now a name this feature's own portal group also uses). T017's own
tests call the view directly rather than through `reverse()` (D21), so it carries no dependency on
T019's landing order.

T019 registered `review-create` at `/assessments/new/` and its access-control tests, mirroring
`review-list`'s own (D16 scoping unchanged: granted-path tests stop at the unrendered
`TemplateResponse`, refusal paths go through the client).

Full suite: 847 passed, 1 skipped, 13 xfailed. `manage.py check` and `makemigrations review --check`
both clean. `poetry run pre-commit run -a` clean.

Next: US-3, the upload and check report.

## 2026-09-16 — US-3 complete (T020, T021, T022+T023, T024)

`review.permissions.can_manage_upload` landed first, its own small slice: the assessment's own
uploader or any Data Curator, nobody else — the object-level rule both new routes share.

T020 built `ReviewUploadView` on Django's plain `DetailView` rather than a `FairDM*` base class
(none of `FairDMCreateView`/`FairDMUpdateView` fit a page backed by two models rather than one
`ModelForm`). GET renders `GHFDBImportForm` (reused from `project/ghfdb/forms.py` rather than
redefined, per the brief); POST reads the uploaded file's bytes once, saves them as a
`SubmittedFile` via `ContentFile`, and calls `import_ghfdb_template(check_only=True)` on the
in-memory bytes rather than re-reading the just-saved `FieldFile` — re-reading it in the same
request risks the underlying stream having already been consumed by the storage write (untested
directly, but cheap to avoid and free of that whole class of flake). D22 records the import-path
correction this needed (`project.ghfdb.*` rather than bare `ghfdb.*`) and the one-line `deptry` fix
it required.

T021 added the counts to `review/upload_report.html`, a partial included from `upload.html` and
tested directly via `render_to_string` the same way T012 tests `review_list_item.html` — the full
page is unaffected by D16's chrome defect, but exercising it through the client isn't necessary
either way once the counts live in their own included template.

T022 built `ReviewConfirmView` (`SingleObjectMixin` + `View`, POST-only): re-runs the check with
`check_only=False` against `review.current.file`, and only stamps `imported_at` and runs
`review.states.confirm_upload` when that re-check comes back clean. D23 explains why T023's
idempotency guard (checking `review.state` before doing any of that) landed in the same commit
rather than as a follow-up. T024 closed the phase: a test enumerating every view class routed in
`review.urls` fails if any of them references the GHFDB import resources directly rather than
through `import_ghfdb_template` — verified as a real guard, not a tautology, by temporarily
reinstating exactly that bypass in `ReviewConfirmView` and watching the test fail before reverting.

Full suite: 871 passed, 1 skipped, 13 xfailed (`-n auto --dist loadscope`, 85s). `manage.py check`
clean; `makemigrations review --check` clean (no model changes this story). `poetry run
pre-commit run -a` clean.

Next: US-4, explaining a failing file in the spreadsheet's own terms.

## 2026-09-16 — US-4 complete (T025, T026, T027, T028)

T025 added the per-failure listing to `upload_report.html`: each `RowFailure` (row, the template's
own column heading, the reason) renders as its own list item, alongside the existing failure count.
Tested by rendering the partial directly with hand-built `GHFDBImportReport`/`RowFailure` objects,
the same way T021 tests the clean-report state.

T026 caught the `ValueError` `import_ghfdb_template` already raises for a header `validate_official_
header` refuses (ADR 0003) — previously unhandled in `ReviewUploadView.post`, so a real file hit an
unhandled 500 rather than a checkable outcome. The view now renders a fixed, translated "the template
is out of date" message instead; nothing from the raised message (which quotes the offending column
names) reaches the page. The refused file is still kept as a `SubmittedFile`, per D7.

T027 needed no production change: the view already builds its report fresh per request with nothing
stored between them, so a corrected re-upload is checked afresh by construction. Per craft-tdd's
probe requirement, this was confirmed rather than assumed — a temporary mutation making the view
merge a stale failure into the next report's `report.failures` was applied, observed to fail the new
test for the right reason, then reverted before committing.

T028's deny-list test found two real FR-013 leaks on its first run, both from `project/ghfdb/report.
py`'s only remaining untranslated seam — the raw `str(exception)` copied into `RowFailure.reason`:
`RelatedModelWidget` (widgets.py) prefixes a wrapped sub-field error with the Django model it is
building (`"HeatFlowSite: Column 'environment': ..."`), and a child row whose parent failed to import
hits Django's own `ForeignKeyWidget` → `Model.DoesNotExist`, whose default message names the model
class directly (`"ParentHeatFlow matching query does not exist."`). `report.py` gained
`_sanitize_reason`: the first case is resolved by keeping only the message from its embedded
`Column '...'` marker onward (already correctly used for column extraction, now reused for the
reason text too); the second is replaced with a generic, still-actionable message pointing at the
row's other reported problem. D25 records this. Both are unit-tested directly in `test_ghfdb/
test_report.py` (mirroring the module that changed) in addition to the deny-list assertion itself in
`test_review/test_views.py`.

Full suite: 882 passed, 1 skipped, 13 xfailed (serial — `-n auto` failed in this sandbox on an
unrelated remote-vocabulary fetch every worker's own Django setup makes, not reproducible serially
and not touched by this story). `manage.py check` clean; `makemigrations --check` shows one
pre-existing unrelated migration in a third-party app (`orbit`), present regardless of this story's
changes since no model changed here. `poetry run pre-commit run -a` clean (this shared worktree's
`end-of-file-fixer` also touched two other stories' brief JSON files each run; reverted both times
rather than committed, per the shared-worktree rule against touching paths outside this story).

Next: US-5, writing the data and deciding who can see it.
