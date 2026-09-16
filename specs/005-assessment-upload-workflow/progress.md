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
