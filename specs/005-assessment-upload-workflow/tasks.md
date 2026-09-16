# Tasks: Upload a completed assessment template through the portal

**Input**: Design documents from `specs/005-assessment-upload-workflow/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: required. Constitution Article VI is non-negotiable and the `review` application has no
tests at all today, so every task writes its failing test first.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel with its neighbours (different files, no shared dependency)
- **[Story]**: the user story the task serves

---

## Phase 1: Foundational (blocking)

**Purpose**: everything every story needs. No story task starts until this phase is green.

- [ ] T001 Create `tests/test_review/` mirroring `project/review/`, with `conftest.py` and an
      `__init__.py` at each level, per Article VI's test-organisation rule.
- [ ] T002 [P] Write `tests/test_review/factories.py`: factory-boy factories for `Review`, a
      claimed `Person`, a ghost `Person`, and a `LiteratureItem`. Reuse the framework's own
      factories where they exist rather than redefining them.
- [ ] T003 Write `project/review/states.py`: the four states from data-model.md as a
      `models.IntegerChoices`, plus the transition functions and the rule that only a curator may
      reach `COMPLETE` from `AWAITING_DECISION`. Tests first, covering every legal transition and
      at least one illegal one per state.
- [ ] T004 Write `project/review/permissions.py`: `is_data_assessor` and `is_data_curator`
      predicates over group membership. Tests first, including a user in neither group and a user
      in both.
- [ ] T005 Data migration creating the `Data Assessor` and `Data Curator` groups. Idempotent, no
      pinned permission primary keys. Delete `project/review/fixtures/ghfdb_review_group.json` and
      the commented `loaddata` hook in `config/settings.py` that refers to it.
- [ ] T006 Extend `review.Review` per data-model.md: `uploaded_by`, `state`, `decided_by`,
      `decided_at`, `decision_comment`. Migrate the existing `status` values into `state` and
      remove `status`. Every field carries `verbose_name` and `help_text` with `gettext_lazy`.
      Tests first.
- [ ] T007 Add `review.SubmittedFile` per data-model.md, with the `current` property on `Review`
      reading the most recent row. Tests first, including an assessment with several submissions.
- [ ] T008 Add `check_only` to `project/ghfdb/importers.py::import_ghfdb_template`, defaulting to
      `False`. Both passes still run for real inside the existing `transaction.atomic()` block, and
      the exit condition becomes `if check_only or outcome.has_errors():
      transaction.set_rollback(True)`. **Do not pass `dry_run=True` to either resource** —
      `specs/004-import-upload-template/decisions.md` D16 records the empirical test showing that it
      hides the parent pass's rows from the child pass and refuses every file, clean ones included.
      Test first, asserting the database is untouched afterwards, the returned outcome still reports
      what would have happened, and a clean multi-site file reports no failures.
- [ ] T009 Write `project/ghfdb/report.py`: turn a `GHFDBImportOutcome` into counts (sites and
      determinations, created and updated separately) and per-row failures carrying the row number,
      the template's own column heading and a specific reason. Column headings come from
      `project/ghfdb/columns.py`. Tests first, using the committed fixtures.
- [ ] T010 Extend the vocabulary failure path so the reason names the supplied value and the
      controlled vocabulary it failed against, satisfying FR-012. Test first, with a file carrying
      a value outside a known vocabulary.

- [ ] T010a Retire the code the new record supersedes, in the same phase that removes `status` and
      the old group, so the tree never holds two answers at once. Delete `ReviewCreateView`,
      `ReviewSubmitView`, `ReviewFilterSet`, `ReviewerListView`, `CreateReviewForm` and
      `SubmitReviewForm`, and the `review-create` and `reviewer-list` routes. Update
      `project/review/admin.py`'s `list_display` and `list_filter` for `state`, and
      `project/review/templates/cotton/review/card.html`, which reads `review.status`. `manage.py
      check` must pass and no reference to `STATUS_CHOICES`, `review__status` or a `Reviewers`
      group may remain. Verify with a grep assertion in the test suite, not by eye.

**Checkpoint**: the record, the states, the roles and the reporting layer all exist and are tested,
and nothing in the tree still reads the vocabulary they replace.

---

## Phase 2: US-1 — The team reaches its own uploads from the portal (P1)

- [ ] T011 [US1] Assessment list view on `FairDMListView`, refusing anyone outside both roles by
      direct URL as well as by navigation. Tests first, covering both roles, a signed-in user in
      neither, and an anonymous visitor.
- [ ] T012 [US1] List template: one row per assessment naming its publication, its uploader and its
      state. Test asserts against the rendered HTML, not the context.
- [ ] T013 [US1] [P] Restore `project/review/menus.py`: the navigation entry, shown only to the two
      roles, carrying the count of assessments waiting on a decision for curators. Test first.
- [ ] T014 [US1] Route registration in `project/review/urls.py` for the list.

**Checkpoint**: the team can reach a list of assessments and nobody else can.

---

## Phase 3: US-2 — An assessment is described before a file is chosen (P1)

- [ ] T015 [US2] Description form: publication, assessors, dates, optional title. Assessors drawn
      from `Person.objects.real()` so unclaimed profiles are selectable. Tests first, including the
      ghost profile case and the end-before-start refusal.
- [ ] T016 [US2] Add-a-publication path on the same form: a bibliography file creates the
      `LiteratureItem` and links it without leaving the page. Test first.
- [ ] T017 [US2] Create view: writes the assessment in `DESCRIBED`, creates the private dataset,
      titles it from the publication when no title is given, records `uploaded_by`, grants the
      uploader object permissions, and credits each assessor as a contributor. Tests first.
- [ ] T018 [US2] Refuse a second assessment against a publication that already has one, naming the
      existing assessment. Test first.
- [ ] T019 [US2] Description template and its route.

**Checkpoint**: an assessment exists with its publication, assessors and an empty private dataset.

---

## Phase 4: US-3 — A file is checked before anything is written (P1)

- [ ] T020 [US3] Upload form and view: store the submission, run the reader with `check_only=True`,
      render the report. The form reuses the `FileExtensionValidator(allowed_extensions=["xlsx"])`
      already on `project/ghfdb/forms.py::GHFDBImportForm` rather than defining a second one. Tests
      first, asserting the dataset still holds no data afterwards and that a non-spreadsheet file is
      refused by the form before the reader sees it.
- [ ] T021 [US3] Report template state showing the counts from T009. Test asserts against rendered
      HTML.
- [ ] T022 [US3] Confirm view, POST only: re-run the check against the stored file, write in the
      same transaction, stamp `imported_at`. Tests first, asserting written counts match reported
      counts.
- [ ] T023 [US3] Idempotent confirmation: a second POST for an assessment already written is a
      no-op redirect. Test first, posting twice.
- [ ] T024 [US3] Prove there is no route that writes without checking: a test that enumerates the
      application's URLs and asserts each write path goes through the check. This is the test for
      SC-002, so it must fail if a future view bypasses the check.

**Checkpoint**: a good file can be checked and confirmed, and nothing writes unchecked.

---

## Phase 5: US-4 — A file that fails is explained in the spreadsheet's own terms (P1)

- [ ] T025 [US4] Failure template state: every failure listed with its row, the template's column
      heading and the reason. Test asserts the rendered text contains the heading as the template
      spells it.
- [ ] T026 [US4] Header refusal path: a file whose header is not the official template's is refused
      on the header alone, with a message naming the template as out of date, and no row-level
      failures reported. Test first, using a file carrying the two misspellings ADR 0003 rejects.
- [ ] T027 [US4] Re-upload against the same assessment: the new file is checked afresh and the
      previous report does not persist. Test first.
- [ ] T028 [US4] Assert no internal field name, model name or traceback reaches the report. Test
      first, by asserting the rendered failure text against a deny list.

**Checkpoint**: a failing file tells its uploader what to fix.

---

## Phase 6: US-5 — Confirming writes the data and decides who can see it (P1)

- [ ] T029 Set the dataset's visibility on confirmation from the uploader's role: a curator's upload
      sets `visibility` to its public value, an assessor's sets nothing and moves the assessment to
      `AWAITING_DECISION`. Tests first, one per role. **Moved into US-6** after US-5 found that
      `Dataset.published` does not exist on the framework version this project resolves, so the
      original two-field instruction could not be carried out. It belongs beside the approval action
      in any case: a curator's confirmation and a curator's approval make a dataset public by the
      same mechanism, and splitting them across two stories split one behaviour in half.
- [ ] T030 [US5] Assert an anonymous visitor cannot reach an assessor's dataset before a decision.
      This is the test for SC-004. Test first.
- [ ] T031 [US5] Assert every submitted file including superseded ones stays retrievable from the
      assessment. Test first.
- [ ] T032 [US5] Assert the reviewer columns in the template contribute nothing, and the named
      assessors stand. Test first.

**Checkpoint**: the trust distinction between the roles is real and proven.

---

## Phase 7: US-6 — A curator decides on an assessor's upload (P2)

- [ ] T033 [US6] Queue view listing assessments in `AWAITING_DECISION`, curators only. Tests first,
      including an assessor being refused.
- [ ] T034 [US6] Approve action: dataset becomes public, assessment reaches `COMPLETE`, and
      `decided_by` and `decided_at` are recorded. Tests first.
- [ ] T035 [US6] Send-back action: dataset stays private, the comment is recorded and shown to the
      uploader, and the assessment moves to `CHANGES_REQUESTED` and accepts a replacement file.
      Tests first.
- [ ] T036 [US6] Refuse an approval from anyone who is not a curator, including the uploader
      themselves. Test first.
- [ ] T037 [US6] Queue and decision templates, and their routes.

**Checkpoint**: the full workflow runs end to end for both roles.

---

## Documentation is part of each story, not a phase at the end

**Amended 2026-09-16, after US0.** The original plan deferred every page to Phase 8. The machine
gate runs a documentation step at each stage exit, and it went red the moment US0 landed: nine new
public names that no page documents, plus `docs/guides/importing-data.md` describing an
`import_ghfdb_template` whose signature had changed under it.

The rule the org already holds is that a story's own documentation is part of that story. So each
story below documents what it adds, in the same commit range, and Phase 8 keeps only the two
vocabulary files that describe the feature as a whole.

- [ ] T010b Document what US0 introduced: the assessment record and its states, the two role
      predicates, the checking mode and the failure report. Update
      `docs/guides/importing-data.md`, which documents `import_ghfdb_template` and was not touched
      when its signature changed. `forge verify --steps docs` must be green.

## Phase 8: Vocabulary

- [ ] T038 [P] `CONTEXT.md`: add Data Assessor and Data Curator, retire "Reviewer" and "data
      administrator", and keep the rule against writing "review" unqualified.
- [ ] T039 [P] `docs/ROADMAP.md`: mark R6 delivered, narrow R7 to contribution from outside the
      team, and strike its deliverable placing team members outside the gate.
- [ ] T040 [P] `docs/guides/`: the team's own page for this workflow, covering what each role may do
      and what to do when a file is refused. Include the outdated-template refusal, because it is
      what they will hit first. This is the reader-facing guide; the per-name reference each story
      writes as it goes is a different thing and is not deferred to here.
- [ ] T041 Run `tests/test_docs` and `forge verify --steps docs` and reconcile anything the new
      pages break.

---

## Dependencies

- Phase 1 blocks everything.
- US-1 and US-2 are independent of each other once Phase 1 is done.
- US-3 depends on US-2 (an assessment must exist to upload against).
- US-4 depends on US-3 (the report must render before its failure state can).
- US-5 depends on US-3 (confirmation must exist before visibility can hang off it).
- US-6 depends on US-5 (something must be waiting before it can be decided).
- Phase 8 depends on everything it documents.

## Watch items carried from the design

- The header refusal in T026 is the feature's known blocker. It is tested as correct behaviour, and
  the guide in T040 says plainly what a user should do about it.
- `Person.is_data_admin` stays pointed at "Data Administrators". Nothing in this feature renames
  that group, and no task should quietly do so.
- The dataset visibility default is private in both framework fields. No task should add code that
  sets private explicitly, because the safe outcome is the one that happens when nothing runs.
- `dry_run=True` is forbidden on either import pass, for the reason recorded in T008. A future
  reader of `importers.py` will find the naive version tempting; the comment there has to say why it
  is wrong, not just what to do instead.
- The design review noted that `SubmittedFile.file` has no explicit size bound. The extension bound
  is covered by T020. The size bound is Django's `DATA_UPLOAD_MAX_MEMORY_SIZE`, left at its default:
  the uploaders are a team of roughly ten signed-in colleagues, and an upload template is a few
  hundred rows. If this application ever accepts files from outside that group, the bound becomes a
  real decision rather than an inherited default.
