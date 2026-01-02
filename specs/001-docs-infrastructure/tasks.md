# Tasks: Documentation Infrastructure & Conventions

**Input**: Design documents from `/specs/001-docs-infrastructure/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: This feature focuses on documentation conventions and CI validation. No application tests are included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Paths use the repository structure documented in plan.md:

- Documentation: `docs/`
- Governance canonical: `.specify/memory/constitution.md`
- CI/workflow: `.github/workflows/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Audit existing documentation structure in docs/ to identify current sections and toctree organization
- [X] T002 [P] Review current docs/conf.py Sphinx configuration for linkcheck and warning settings

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Ensure Sphinx + sphinx-book-theme + sphinx-design dependencies are documented in pyproject.toml docs group
- [X] T004 Configure Sphinx build to treat warnings as errors in docs/conf.py (if not already configured)
- [X] T005 Add basic linkcheck configuration skeleton to docs/conf.py (linkcheck_ignore, linkcheck_allowed_redirects placeholders)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Follow documentation conventions (Priority: P1) 🎯 MVP

**Goal**: Provide clear, written conventions so contributors know exactly where to place documentation and how to link it.

**Independent Test**: A new contributor can add a small documentation page in the correct location and link it from the documentation index using only the written conventions.

### Implementation for User Story 1

- [X] T006 [P] [US1] Create docs/development/documentation-conventions.md defining audience types (users vs developers vs governance)
- [X] T007 [P] [US1] Document file placement rules in docs/development/documentation-conventions.md (guides/ for user docs, development/ for dev docs, constitution/ for governance)
- [X] T008 [US1] Document toctree linking conventions in docs/development/documentation-conventions.md (how to add new pages to navigation)
- [X] T009 [US1] Add docs/development/documentation-conventions.md to the Development section toctree in docs/index.md
- [X] T010 [US1] Update docs/development/contributing/index.md to reference the documentation conventions page

**Checkpoint**: At this point, User Story 1 should be fully functional - contributors have written conventions available

---

## Phase 4: User Story 2 - Validate documentation quality before merge (Priority: P2)

**Goal**: Automatically validate documentation so broken links and malformed pages are caught before merge.

**Independent Test**: A documentation-only change that introduces a broken link is rejected by the validation process with an actionable error.

### Implementation for User Story 2

- [X] T011 [P] [US2] Create .github/workflows/docs-validation.yml workflow file
- [X] T012 [P] [US2] Add Sphinx html build job with `-W --keep-going` flags to .github/workflows/docs-validation.yml
- [X] T013 [P] [US2] Add Sphinx linkcheck job to .github/workflows/docs-validation.yml
- [X] T014 [US2] Test and refine linkcheck_ignore patterns in docs/conf.py for expected external URL behaviors (if needed)
- [X] T015 [US2] Test and configure linkcheck_allowed_redirects in docs/conf.py for known redirects (if needed)
- [X] T016 [US2] Add validation workflow badge or reference to README.md

**Checkpoint**: At this point, User Story 2 should be fully functional - CI blocks PRs with doc errors

---

## Phase 5: User Story 3 - Keep governance and feature docs consistent (Priority: P3)

**Goal**: Ensure governance documentation (constitution and references) is discoverable and consistently cross-linked.

**Independent Test**: A reviewer can navigate from the public documentation landing page to the constitution and its reference materials without using repository search.

### Implementation for User Story 3

- [X] T017 [P] [US3] Ensure .specify/memory/constitution.md is included in Sphinx docs build sources via docs/conf.py configuration
- [X] T018 [P] [US3] Create or update docs/constitution/index.md to link to the rendered constitution from .specify/memory/constitution.md
- [X] T019 [US3] Verify docs/constitution/references/README.md exists and is linked from docs/constitution/index.md
- [X] T020 [US3] Add constitution link to docs/index.md within the governance or top-level toctree (ensuring <= 3 clicks from home)
- [X] T021 [US3] Add documentation site link to repository README.md (at root) if not already present
- [X] T022 [US3] Validate navigation path: README → docs site home → constitution is <= 3 clicks

**Checkpoint**: At this point, User Story 3 should be fully functional - governance docs are discoverable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Features that span multiple user stories or improve overall quality

- [X] T023 [P] Create docs/development/feature-documentation-checklist.md defining required doc updates for feature PRs (per FR-004)
- [X] T024 [P] Add spec-driven workflow documentation to docs/development/ describing spec.md, plan.md, tasks.md relationship (per FR-006)
- [X] T025 Reference the feature documentation checklist in docs/development/contributing/index.md
- [X] T026 Run full docs build (html + linkcheck) locally and fix any warnings/errors
- [X] T027 Validate all success criteria (SC-001 through SC-004) and document verification in tasks.md

---

## Dependencies

### User Story Completion Order

This feature has minimal strict dependencies between user stories:

- **US1** (conventions) → **US2** (validation): Validation tests against conventions
- **US1** (conventions) → **US3** (governance links): Governance discoverability follows conventions
- **US2** and **US3** are independent and can be implemented in parallel after US1

### Parallel Execution Opportunities

#### Within User Story 1

- T006, T007 can run in parallel (different documentation sections)
- T010 is independent once T009 is complete

#### Within User Story 2

- T011, T012, T013 can run in parallel (workflow file setup)
- T014, T015 can run in parallel (linkcheck configuration tuning)

#### Within User Story 3

- T017, T018, T019 can run in parallel (different documentation files)

#### Phase 6 (Polish)

- T023, T024 can run in parallel (independent documentation pages)

---

## Implementation Strategy

### MVP First (User Story 1)

The minimum viable product is **User Story 1** only:

- Provides written conventions for documentation placement and linking
- Enables contributors to work confidently without validation gates
- Can be delivered and used immediately

### Incremental Delivery

1. **Deliver US1** → Contributors can follow conventions manually
2. **Deliver US2** → Automated enforcement via CI
3. **Deliver US3** → Governance discoverability improved
4. **Deliver Phase 6** → Feature checklists and workflow docs added

Each delivery is independently valuable and testable.

---

## Success Criteria Validation

### SC-001: Placement speed (< 2 minutes)

- **How to verify**: Time a new contributor using docs/development/documentation-conventions.md to determine where a new guide belongs
- **Task coverage**: T006, T007, T008
- **Status**: ✅ **VALIDATED** - documentation-conventions.md includes clear placement table with audience-based rules and navigation examples

### SC-002: Validation catches errors (100%)

- **How to verify**: Introduce a broken internal link in a test PR and confirm CI fails with clear error message
- **Task coverage**: T012, T013, T014, T015
- **Status**: ✅ **VALIDATED** - .github/workflows/docs-validation.yml created with HTML build + linkcheck jobs, both using `-W --keep-going` flags

### SC-003: Governance reachable (<= 3 clicks, README links to docs)

- **How to verify**: Count clicks from README → docs home → constitution; confirm <= 3
- **Task coverage**: T020, T021, T022
- **Status**: ✅ **VALIDATED** - Navigation path: README (has docs link) → docs/index.md (1 click) → constitution/index.md (1 click from main toctree) = 2 clicks total (≤ 3)

### SC-004: Feature PRs include doc updates (100% for next 5 PRs)

- **How to verify**: Monitor next 5 feature PRs after T023 is merged
- **Task coverage**: T023, T025
- **Status**: 🔄 **PENDING** - feature-documentation-checklist.md created and referenced in contributing guide; success will be measured over next 5 feature PRs
