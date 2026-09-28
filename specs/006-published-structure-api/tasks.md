# Tasks: The published structure reachable through the API

**Input**: Design documents from `specs/006-published-structure-api/`

**Prerequisites**: plan.md, spec.md, research.md

**Tests**: required. Every task writes its failing test first (Article I). Test modules mirror the
source module they exercise and group tests in `Test<Subject>` classes; data comes from
`tests/factories.py`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel with its neighbours (different files, no shared dependency)
- **[Story]**: the user story the task serves

---

## Phase 1: User Story 1 — Parents read through the API (P1)

**Goal**: `/api/v1/ghfdb/parents/` and `/api/v1/ghfdb/parents/<ID_parent>/`.

**Independent test**: build published parents with determinations, request both routes with no
credentials, and assert the key set and order, the counts, and a constant query count per page.

- [ ] T001 [US1] In `project/ghfdb/serializers.py`, add `PublishedValueField`, `ConceptLabelsField`
      and `published_fields(columns, overrides=None)` per plan.md. Tests first in
      `tests/test_ghfdb/test_serializers.py`: a quantity renders as a float, `None` and `""` render
      as `null`, a many-valued column renders a list of labels, a `None` on the path renders `[]`,
      and the builder returns every requested column in the order given, reading accessors from
      `PublishedColumns.ENTRIES`, with an override replacing one accessor.
- [ ] T002 [US1] In `project/ghfdb/managers.py`, narrow `with_child_counts()` to determinations
      carrying a published identifier (research R9). Test first in
      `tests/test_ghfdb/test_managers.py`: a parent with one published and one unpublished
      determination counts one.
- [ ] T003 [US1] Add the parent record serializer and the parent viewset (`project/ghfdb/viewsets.py`,
      with the shared base described in plan.md), and register it in `project/ghfdb/urls.py`. Tests
      first in `tests/test_ghfdb/test_viewsets.py` covering US1 scenarios 1–8 and the edge cases
      (a page past the end is a 404, an oversized page size is capped, a non-numeric identifier is
      a 404, a duplicated identifier resolves to the earliest record, a signed-in request succeeds,
      a record in a private dataset is absent for an anonymous request), and in
      `tests/test_ghfdb/test_urls.py` for scenario 9 (listed in the API index, present in the
      schema). Key order asserted against `PARENT_COLUMNS` itself, never a copy.
- [ ] T004 [US1] Write `docs/guides/published-structure-api.md` with the introduction, paging, and
      the parents section with a worked request and response, and link it from the docs index.

**Checkpoint**: parents are served, documented and green. US1 is independently shippable.

---

## Phase 2: User Story 2 — Determinations read through the API (P1)

**Goal**: `/api/v1/ghfdb/children/` and `/api/v1/ghfdb/children/<ID>/`.

- [ ] T005 [US2] Add the determination list and detail serializers and the determination viewset,
      and register it. Tests first in `tests/test_ghfdb/test_viewsets.py` covering US2 scenarios
      1–9 and the edge cases (no coordinates still returned with them empty, many-valued columns
      with no members are `[]`, signed-in request, private dataset, neither of
      `REJECTED_MISSPELLED_COLUMNS` anywhere in the body), and in `test_urls.py` for
      scenario 10, asserting the schema carries both determination shapes.
- [ ] T006 [US2] Replace the parent detail's attached determination links with the determination
      list record from T005, keeping the parent detail's query count constant. Test first: the
      attached records carry the determination list keys.
- [ ] T007 [US2] Add the determinations section to the consumer guide, with a worked list request
      and a worked single-record response showing the nested parent.

**Checkpoint**: parents and determinations are served and navigable both ways.

---

## Phase 3: User Story 3 — The released row served as it is published (P1)

**Goal**: `/api/v1/ghfdb/flat/` and `/api/v1/ghfdb/flat/<ID>/`.

- [ ] T008 [US3] In `project/ghfdb/managers.py`, annotate `quality_parent` on the child queryset's
      `as_ghfdb_flat()` from `parent__quality`. Test first in `test_managers.py`.
- [ ] T009 [US3] Add the flat row serializer (with the `explo_purpose` override) and the flat
      viewset, and register it. Tests first in `test_viewsets.py` covering US3 scenarios 1–8,
      asserting the row's keys equal `PARENT_COLUMNS + CHILD_COLUMNS` read from `constants.py`,
      that neither of `REJECTED_MISSPELLED_COLUMNS` appears anywhere in the response body, and a
      constant query count; and in `test_urls.py` for scenario 9.
- [ ] T010 [US3] Add the flat section to the consumer guide, with a worked request and response.

**Checkpoint**: all three endpoints are served, documented and green.
