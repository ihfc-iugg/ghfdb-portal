# Tasks: The published structure reachable through the API

**Input**: Design documents from `specs/006-published-structure-api/`

**Prerequisites**: plan.md, spec.md, research.md

**Tests**: required. Every task writes its failing test first (Article I). Test modules mirror the
source module they exercise and group tests in `Test<Subject>` classes. Data comes from
`tests/factories.py` and the helpers already in `tests/test_ghfdb/conftest.py`
(`build_published_chain`, `build_child`, `constant_query_count`), never inline construction.

A query-count test compares a page of one record with a page of the maximum size (SC-003). A write
test asserts the request is refused and nothing changed, without pinning which refusal status the
framework answers with.

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
- [ ] T002 [US1] Add the parent record serializer and the parent viewset in
      `project/ghfdb/viewsets.py` (with the shared base described in plan.md), and register it in
      `project/ghfdb/urls.py`. Tests first in `tests/test_ghfdb/test_viewsets.py` covering US1
      scenarios 1–4 and 6–8, scenario 5 up to "the same parent is returned" (its attached
      determinations are T005's), and the edge cases: a page past the end is a 404, an oversized
      page size is capped, a non-numeric identifier is a 404, a signed-in request succeeds, and a
      parent in a private dataset is absent from the list and a 404 on its own route for an
      anonymous request. Scenario 9 in `tests/test_ghfdb/test_urls.py` (listed in the API index,
      present in the schema). Key order asserted against `PARENT_COLUMNS` itself, never a copy.
- [ ] T003 [US1] Write `docs/guides/published-structure-api.md` with the introduction, paging, the
      anonymous request limit, and the parents section with a worked request and response. Say that
      a parent's counts include determinations the API does not list (D13). Link it from the docs
      index.

**Checkpoint**: parents are served, documented and green.

---

## Phase 2: User Story 2 — Determinations read through the API (P1)

**Goal**: `/api/v1/ghfdb/children/` and `/api/v1/ghfdb/children/<ID>/`.

- [ ] T004 [US2] Add the determination list and detail serializers and the determination viewset,
      narrowed to determinations whose parent the parent route serves to the same requester (D16),
      and register it. Tests first in `tests/test_ghfdb/test_viewsets.py` covering US2 scenarios
      1–9, with keys asserted against `CHILD_COLUMNS` followed by `ID`, and the edge cases: no
      coordinates still returned with them empty, many-valued columns with no members are `[]`,
      signed-in request, neither of `REJECTED_MISSPELLED_COLUMNS` anywhere in the body, a
      determination in a private dataset absent from the list and a 404 on its own route, a
      published determination whose parent is in a private dataset absent for an anonymous
      request, and a determination whose parent carries no published identifier absent. Scenario
      10 in `test_urls.py`, asserting the schema carries both determination shapes.
- [ ] T005 [US2] Attach `children` to the parent detail: the determination queryset passed through
      the visibility filter for the requester, in the determination list shape, keeping the parent
      detail's query count constant (D16). Tests first: US1 scenario 5 in full, and a published
      determination in a private dataset under a public parent absent from the anonymous parent
      detail.
- [ ] T006 [US2] Add the determinations section to the consumer guide, with a worked list request
      and a worked single-record response showing the nested parent.

**Checkpoint**: parents and determinations are served and navigable both ways.

---

## Phase 3: User Story 3 — The released row served as it is published (P1)

**Goal**: `/api/v1/ghfdb/flat/` and `/api/v1/ghfdb/flat/<ID>/`.

- [ ] T007 [US3] In `project/ghfdb/managers.py`, annotate `quality_parent` on the child queryset's
      `as_ghfdb_flat()` from `parent__quality`. Test first in `tests/test_ghfdb/test_managers.py`.
- [ ] T008 [US3] Add the flat row serializer (with the `explo_purpose` and `ID` overrides) and the
      flat viewset over the determination route's queryset, and register it. Tests first in
      `test_viewsets.py` covering US3 scenarios 1–8, asserting the row's keys equal
      `PARENT_COLUMNS + CHILD_COLUMNS + ["ID"]` built from `constants.py` and in the order
      `GHFDB_COLUMN_ORDER` gives them, that neither of `REJECTED_MISSPELLED_COLUMNS` appears
      anywhere in the response body, and a constant query count. Scenario 9 in `test_urls.py`.
- [ ] T009 [US3] Add the flat section to the consumer guide, with a worked request and response.

**Checkpoint**: all three endpoints are served, documented and green.
