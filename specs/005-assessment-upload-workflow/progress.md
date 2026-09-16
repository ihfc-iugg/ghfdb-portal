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

## 2026-09-16 — US-5

T029 is blocked. Its curator branch needs `Dataset.published`, which does not exist on the `fairdm`
dependency version this repository is pinned to — confirmed against the running model class, not
just the docs describing it (D26). No production code was written for either branch of T029: the
assessor branch (dataset stays private, nothing written) is already the framework's own default, and
is exercised as a precondition of the T030 test below rather than duplicated in a T029-only test.

T030, T031 and T032 needed no production code: each is proving a guarantee the framework or an
earlier story's code already provides — `PrivateRecordNotFoundMixin`/`DatasetManager` for T030
(private-by-default visibility, already the outcome of T029's un-implementable-but-also-unneeded
assessor branch), `Review.current`/`SubmittedFile`'s per-submission rows for T031, and `project/ghfdb
/resources`' existing `ACCEPTED_UNSTORED_COLUMNS` handling (FR-009, US-4) for T032. Per craft-tdd's
probing requirement, each was confirmed rather than assumed: a temporary one-line mutation of the
mechanism each test protects (forcing `dataset.visibility` public after confirm for T030, reversing
`Review.current`'s ordering for T031, clearing `review.reviewers` after confirm for T032) was applied
in turn, the corresponding test observed to fail for the right reason, then reverted before running
the suite again and committing. All three land as test-only commits in `tests/test_review/
test_views.py`, the module whose subject (`ReviewConfirmView`/`ReviewUploadView`) each is about.

`poetry run ruff check`/`ruff format --check` on the touched file surfaced two pre-existing `I001`
import-order findings unrelated to anything added here (lines 21 and 764, both present unchanged at
this story's own `verified_base` commit — confirmed by running the same check against `git show
HEAD:tests/test_review/test_views.py`). Left alone, out of scope: AGENTS.md's own "Lint" section
already documents that `pre-commit`'s pinned ruff (which excludes `tests/` entirely) is not what CI
enforces, and these are exactly the kind of gap that split creates. Flagged in the completion report
rather than fixed.

Full suite and the repo's verify commands: see the completion report.

## 2026-09-16 — US-6

T029, moved here from US-5 (D27): confirmed `Dataset` carries `visibility` and nothing named
`published` by importing it from the installed package and printing its fields, per the brief's own
instruction not to take its word for it. `ReviewConfirmView.post` now calls a new
`_publish_if_complete(review)` after the state transition — writes `visibility = PUBLIC` exactly
when the assessment's own state reached `COMPLETE`, so it does not re-implement `is_data_curator`
anywhere; it reads the outcome `review.states.confirm_upload` already computed. Proven by asserting
the field directly on both branches (curator: `PUBLIC`; assessor: still `PRIVATE`, extending the
existing `TestAssessorDatasetVisibility`).

T033: `ReviewQueueView` at `/assessments/queue/`, `is_data_curator`-gated, filtered to
`AWAITING_DECISION`. See D28 for why its template does not use `FairDMListView`'s stock item-card
rendering — the short version is that mechanism strips `request` from the row's context, which is
fine for a read-only card and not fine for the two POST forms T037 adds later.

T034: `ReviewDecideView`, POST only at `/assessments/<pk>/decide/`, `is_data_curator`-gated. The
approve branch calls `review.states.approve` (which still raises `IllegalTransition` for a wrong
state or a non-curator actor — defence in depth, `test_func` is what actually stops the request) then
the same `_publish_if_complete` T029 added, and stamps `decided_by`/`decided_at`.

T035: the same view's `send_back` branch calls `review.states.send_back`, leaves the dataset alone
(private stays private, nothing writes it), and records `decision_comment` alongside
`decided_by`/`decided_at`. The comment reaches the uploader through `ReviewUploadView`'s own context
— added only while the assessment is `CHANGES_REQUESTED`, so a comment from a cycle already resolved
does not linger on the page. The full round trip (send back → replacement upload → confirm → back to
`AWAITING_DECISION`, with the original `SubmittedFile` still present) is proven end to end in
`TestReviewSendBackRoundTrip`, reusing the existing upload/confirm routes rather than adding
anything new to them.

T036: one dedicated test proves an assessor cannot approve their own upload through this route —
`review-decide` is gated by `is_data_curator` alone, never `can_manage_upload`, unlike upload/
confirm. Per craft-tdd's probing rule, checked as a real guard rather than assumed: `test_func` was
temporarily widened to also allow the uploader, the test observed to fail for the right reason (a
302 in place of the expected 403), then reverted before committing.

T037: `review_queue_item.html` gained the approve and send-back forms once `review-decide` existed to
point them at (D28 explains why they live in the include rather than the auto-rendered card).
Route-resolution tests for both `review-queue` and `review-decide` were added to `test_urls.py`,
mirroring T014's role for T011's already-wired route — the URLs themselves landed with their views'
own commits (T033/T034), same shape as `review-list`/`review-create`.

No notification framework, model or dependency was added (D8): the queue itself and the badge count
T013 already built on the navigation entry are what FR-022 asks for.

Full suite, `manage.py check`, `makemigrations --check`, and `poetry run pre-commit run -a`: see the
completion report.

## 2026-09-16 — Phase 8 complete (T038, T039, T040, T041)

T038 retired "Reviewer" and "data administrator" from `CONTEXT.md`, replacing the single Reviewer
entry with a Data Assessor entry and a new Data Curator entry, and pointed "Publication approval" at
Data Curator. Noted in passing: the model's own `reviewers` field and `heat_flow_reviews` related
name keep their pre-rename spelling (D3), so the glossary says so rather than leaving a reader to
find the mismatch themselves.

T039 marked R6 delivered and rewrote it as prose describing what the portal now does, matching R1/
R2/R4's own delivered convention rather than keeping its "Deliverables"/"Out of scope" bullets with
only a status tag changed. R7 narrowed to the one thing it still lacks — a route into the existing
role/gate/queue mechanism for someone holding neither role — dropping the "Datasets from team
members published without waiting" deliverable D2 superseded, along with the three deliverables
this feature already built. D29 records both calls.

T040 added `docs/guides/assessment-uploads.md`: what each role may do, describing an assessment,
reading a check report row by row, and the two decision actions a curator can take. States plainly,
near the top rather than buried, that a file produced from today's distributed template is refused
on its header until the template is corrected upstream (ADR 0003) — the first thing the team will
hit. Linked from `docs/index.md`'s Guides toctree (D29 on why not also from
`guides/introduction.md`).

T041: `poetry run pytest tests/test_docs` — 305 passed. `python3 kit/forge verify --steps docs
--base df3ccba` — passed. `poetry run sphinx-build -b html docs docs/_build/html -W --keep-going` —
45 warnings, all pre-existing (confirmed identical count and content against the unmodified base
commit). Full suite: 908 passed, 1 skipped, 13 xfailed, matching the brief's `verified_base` count
exactly. `manage.py check` clean. `poetry run pre-commit run -a` clean, once one unrelated
`end-of-file-fixer` touch to `us6-brief.json` — another orchestrator's file in this shared worktree
— was reverted rather than committed.

No Python changed anywhere in this phase.
