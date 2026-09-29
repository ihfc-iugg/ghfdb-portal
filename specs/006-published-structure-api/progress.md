# Progress — 006 published structure API

## 2026-09-29

- Picked up off the queue. Branch reset to `origin/main` at 720f559, which carries the merged
  specification.
- Baseline verify green on 720f559: lint, typecheck, test, build, conformance, docs.
- Plan, research and tasks written. Three stories, ten tasks, no migration.
- Design review: one reviewer, three lenses, request changes. One high finding (records reached
  through the parent–determination relation bypassed the visibility filter) and four medium ones,
  all applied as plan edits: D12, D13, D15, D16 and D17 rewritten or added, tasks renumbered to
  nine.

## 2026-09-28T23:27:11Z · Implementer US1 · T001

- Did: added `PublishedValueField`, `ConceptLabelsField` and `published_fields(columns, overrides)`
  to `project/ghfdb/serializers.py`, per plan.md's serializer-builder design.
- Verified: `uv run pytest tests/test_ghfdb/test_serializers.py -n0 -q` — 8 passed. `uv run
  pre-commit run --files project/ghfdb/serializers.py tests/test_ghfdb/test_serializers.py` — all
  hooks passed (ruff, mypy, deptry). Covers T001's acceptance scenarios (SC- none named for this
  task; it is the shared builder US2/US3 reuse).
- Next: T002, the parent serializer and viewset.
- Watch: `PublishedColumns.ENTRIES` accessors that equal the published column name (the common case)
  must not be passed as an explicit `source=` — DRF's `Field.bind()` refuses a `source` equal to the
  field name. Recorded as D18.

## 2026-09-28T23:27:11Z · Implementer US1 · T002

- Did: added `GHFDBParentSerializer` to `serializers.py`; added `project/ghfdb/viewsets.py` with
  `GHFDBBaseViewSet` and `GHFDBParentViewSet`; registered `ghfdb/parents` on `fairdm_api_router` in
  `project/ghfdb/urls.py`; added a `public_dataset` fixture to `tests/test_ghfdb/conftest.py`
  (design-review watch item — `DatasetFactory` defaults to `Visibility.PRIVATE`).
- Verified: `uv run pytest tests/test_ghfdb/test_viewsets.py tests/test_ghfdb/test_urls.py
  tests/test_ghfdb/test_serializers.py -n0 -q` — 26 passed. `uv run pre-commit run --files
  project/ghfdb/serializers.py project/ghfdb/viewsets.py project/ghfdb/urls.py
  tests/test_ghfdb/test_viewsets.py tests/test_ghfdb/test_urls.py tests/test_ghfdb/conftest.py` —
  all hooks passed. Covers US1 scenarios 1–4, 6–8, scenario 5 up to "the same parent is returned"
  (SC-003, SC-006, D12, D13, D14, D16 watch on private-dataset parents); scenario 9 in
  `test_urls.py` (API index + schema).
- Next: T003, the consumer guide.
- Watch: an anonymous write is answered 401 before the read-only viewset's own 405 would apply
  (`FairDMObjectPermissions.has_permission` runs in `initial()`, before handler dispatch) — observed
  directly in the test run's captured log, matches the design-review watch item; tests assert
  `status_code >= 400` rather than pinning one status.

## 2026-09-28T23:27:11Z · Implementer US1 · T003

- Did: wrote `docs/guides/published-structure-api.md` — introduction naming all three endpoints,
  paging, the anonymous rate limit and what it means for reading the whole database, and the
  `parents` section with a worked request/response and the child-counts note (D13). Linked it from
  `docs/index.md`'s Guides toctree.
- Verified: `uv run pre-commit run --files docs/index.md docs/guides/published-structure-api.md` —
  all hooks passed (only `deptry` runs on markdown; no reformatting). Sphinx itself is not installed
  in this worktree's `.venv` (`docs` is a separate dependency group), so the page was checked by eye
  against the toctree's existing entries rather than built; the full verify's `docs` step is the
  first point this run can confirm the build.
- Next: none — US1 (T001–T003) is complete pending the story's full verify (§5).
- Watch: `docs/guides/published-structure-api.md` intentionally names `children` and `flat` as
  endpoints that do not exist yet ("get their own sections as they are built") — US2/US3 add to this
  same file rather than replacing it (tasks.md T006, T009).

## 2026-09-29T00:04:02Z · Implementer US2 · T004

- Did: added `GHFDBChildListSerializer` and `GHFDBChildDetailSerializer` to `serializers.py`
  (`parent` built in `get_fields()` rather than declared as a class attribute — it would shadow
  DRF's own `Field.parent`); added `GHFDBChildViewSet` to `viewsets.py`, narrowed to determinations
  whose parent the parent route's own queryset serves to the requester, as a subquery (spec D16);
  registered `ghfdb/children` on `fairdm_api_router` in `urls.py`.
- Verified: `uv run pytest tests/test_ghfdb/test_viewsets.py tests/test_ghfdb/test_urls.py
  tests/test_ghfdb/test_serializers.py -n0 -q` — 49 passed. `uv run pre-commit run --files
  project/ghfdb/serializers.py project/ghfdb/viewsets.py project/ghfdb/urls.py
  tests/test_ghfdb/test_viewsets.py tests/test_ghfdb/test_urls.py` — all hooks passed. Covers US2
  scenarios 1-9 in `test_viewsets.py`; scenario 10 in `test_urls.py`.
- Next: T005, attaching `children` to the parent detail.
- Watch: `tests/test_ghfdb/conftest.py`'s `constant_query_count` fixture is flaky independent of
  this story — reproduced on the unmodified US1 baseline too (2 failures in 4 repeated runs of
  `test_viewsets.py` + `test_urls.py` + `test_serializers.py` together, none when run alone). An
  installed request/query logger (`orbit_orbitentry`) writes a variable number of rows per request
  depending on cache state, and those writes count toward `CaptureQueriesContext`'s total. Isolated,
  repeated runs of this story's own query-count tests showed identical, matching query lists at both
  measurement points. Not fixed here — outside this story's scope and predates it.

## 2026-09-29T00:12:40Z · Implementer US2 · T005

- Did: added `GHFDBParentDetailSerializer` to `serializers.py`, inserting `children` between the
  declared keys and the published columns (reads `children_list` — the proxy's own `children` is the
  model's real reverse relation manager, which cannot be reassigned to a filtered queryset); wired it
  onto `GHFDBParentViewSet`'s single-record route in `viewsets.py`, which now reuses
  `GHFDBChildViewSet`'s own queryset (through its filter backends, then narrowed to this parent), so
  the attached list matches what `/children/` would serve the same requester for that parent.
- Verified: `uv run pytest tests/test_ghfdb/test_viewsets.py tests/test_ghfdb/test_urls.py
  tests/test_ghfdb/test_serializers.py -n0 -q` — 51 passed, 1 failed (see below). `uv run pre-commit
  run --files project/ghfdb/serializers.py project/ghfdb/viewsets.py
  tests/test_ghfdb/test_viewsets.py` — all hooks passed. New tests cover US1 scenario 5 in full, the
  cross-dataset case (a published determination in a private dataset under a public parent), and the
  parent detail's query count against a growing number of attached determinations.
- Next: T006, the consumer guide's determinations section.
- Blocked: `TestGHFDBParentViewSet::test_following_the_self_link_returns_the_same_parent`, a
  pre-existing test not authored in this story, now fails — it asserts the parent detail equals the
  list record verbatim, which predates this story's requirement (this feature's own specification)
  that the single-record route also carry the parent's determinations. Not modified, per the
  standing rule against touching a test from an earlier story. The fix is small and already proven
  by the new test added alongside it in the same commit
  (`test_following_the_self_link_returns_the_parent_with_its_determinations_attached`): the old
  test's final assertion needs to compare the fields the two shapes still share, or assert `children`
  separately, rather than comparing the two response bodies for exact equality.

## 2026-09-29T00:16:03Z · Implementer US2 · T006

- Did: added a "Determinations" section to `docs/guides/published-structure-api.md`, with a worked
  list request and a worked single-record response showing the nested parent; added a worked parent
  single-record response to the "Parents" section showing its attached `children`; extended
  "Implementation notes" with `GHFDBChildListSerializer`, `GHFDBChildDetailSerializer`,
  `GHFDBParentDetailSerializer` and `GHFDBChildViewSet`.
- Verified: `uv run pre-commit run --files docs/guides/published-structure-api.md` — all hooks
  passed (deptry only; no markdown reformatting configured, matching T003). Every JSON block was
  checked against the shapes the viewsets and serializers actually built in this story, and each
  JSON code block parses (checked with `json.loads`, excluding the pre-existing paging example's
  `[ ... ]` placeholder). Sphinx itself is not installed in this worktree's `.venv`, same as T003 —
  the full verify's `docs` step is the first point this run can confirm the build.
- Next: none — US2 (T004–T006) is complete, T005 blocked pending the fix to one pre-existing test
  (see its own entry above).
