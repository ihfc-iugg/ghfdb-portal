# Tasks: Testing Infrastructure & Conventions

**Feature**: specs/002-testing-infrastructure/
**Input**: [spec.md](spec.md), [plan.md](plan.md)
**Created**: 2026-01-05

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **Checkbox**: `- [ ]` for pending, `- [x]` for complete
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1-US5) for traceability
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, pytest configuration, and directory structure

- [x] T001 Create tests/contracts/ directory with **init**.py for contract tests
- [x] T002 Update pyproject.toml with pytest markers (integration, contract, slow, external)
- [x] T003 Update pyproject.toml with pytest test discovery configuration (default to unit tests only)
- [x] T004 Add pytest-cov configuration to pyproject.toml (80% coverage threshold, omit migrations/tests)
- [x] T005 Update tests/README.md with test layer definitions and marker usage guide

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core fixtures and conftest infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create fixtures/minimal_ghfdb_import.xlsx with 5 heat flow sites (complete mandatory fields)
- [x] T007 Create fixtures/invalid_ghfdb_import.xlsx with 5 validation error cases (missing fields, invalid ranges)
- [x] T008 Create fixtures/review_submission_dataset.json Django fixture (dataset in pending review state with provenance)
- [x] T009 Create fixtures/admin_approval_dataset.json Django fixture (dataset in reviewed state ready for approval)
- [x] T010 Create fixtures/round_trip_reference.xlsx with 10 heat flow sites covering all GHFDB field types
- [x] T011 Create fixtures/README.md documenting each fixture's purpose, content, and update process
- [x] T012 Extend tests/conftest.py with pytest fixtures for loading minimal_ghfdb_import fixture
- [x] T013 [P] Extend tests/conftest.py with pytest fixtures for loading invalid_ghfdb_import fixture
- [x] T014 [P] Extend tests/conftest.py with pytest fixtures for loading review/approval workflow fixtures

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Feature Developer Writes Unit Tests (Priority: P1) 🎯 MVP

**Goal**: Enable developers to write fast, isolated unit tests following clear conventions

**Independent Test**: Create a sample unit test module, run with pytest, verify <5 second execution

### Documentation for User Story 1

- [ ] T015 [US1] Create docs/guides/testing-standards.md with test pyramid introduction and TDD workflow section
- [X] T016 [US1] Add unit test conventions section to testing-standards.md (file organization, naming patterns)
- [X] T017 [US1] Add unit test database policy section to testing-standards.md (when to use @pytest.mark.django_db)
- [X] T018 [US1] Add parametrized test pattern examples to testing-standards.md with 3-5 code samples
- [X] T019 [US1] Add fixture naming conventions section to testing-standards.md (lowercase_with_underscores, scope usage)

### Example Unit Tests for User Story 1

- [X] T020 [P] [US1] Create example unit test in tests/test_heat_flow/test_validation.py for temperature range validation
- [X] T021 [P] [US1] Create example parametrized unit test in tests/test_heat_flow/test_coordinates.py for coordinate normalization
- [X] T022 [P] [US1] Create example unit test in tests/test_heat_flow/test_quality_scores.py for U-score calculation with known values

**Checkpoint**: Unit test conventions documented and validated with working examples

---

## Phase 4: User Story 2 - QA Engineer Validates Import-to-Export Workflow (Priority: P1) 🎯 MVP

**Goal**: Enable full-stack integration testing of import → review → approval → export workflow

**Independent Test**: Run `pytest -m integration`, verify complete workflow executes in <2 minutes

### Documentation for User Story 2

- [ ] T023 [US2] Add integration test conventions section to docs/guides/testing-standards.md (workflow testing patterns)
- [ ] T024 [US2] Add integration test fixture usage guide to testing-standards.md (how to use minimal fixtures in tests)
- [ ] T025 [US2] Add integration test assertion strategies to testing-standards.md (state transitions, data preservation checks)

### Implementation for User Story 2

- [ ] T026 [P] [US2] Create tests/test_ghfdb/test_import_workflow_integration.py with @pytest.mark.integration marker
- [ ] T027 [US2] Implement test_import_minimal_dataset_happy_path in test_import_workflow_integration.py (uses minimal_ghfdb_import fixture)
- [ ] T028 [US2] Implement test_import_invalid_dataset_raises_validation_errors in test_import_workflow_integration.py (uses invalid_ghfdb_import fixture)
- [ ] T029 [P] [US2] Create tests/test_review/test_review_workflow_integration.py with @pytest.mark.integration marker
- [ ] T030 [US2] Implement test_submit_for_review_state_transition in test_review_workflow_integration.py (uses review_submission_dataset fixture)
- [ ] T031 [US2] Implement test_approve_for_publication_requires_admin in test_review_workflow_integration.py (uses admin_approval_dataset fixture, tests authorization)
- [ ] T032 [US2] Implement test_export_without_approval_fails in test_import_workflow_integration.py (validates approval gate)
- [ ] T033 [US2] Implement test_full_workflow_import_to_export in test_import_workflow_integration.py (end-to-end happy path, asserts 5 sites exported)

**Checkpoint**: Integration test suite validates complete data lifecycle with minimal fixtures

---

## Phase 5: User Story 3 - API Consumer Verifies Contract Stability (Priority: P2)

**Goal**: Enable contract testing to detect API breaking changes before release

**Independent Test**: Run `pytest -m contract`, verify API responses match documented schemas

### Documentation for User Story 3

- [ ] T034 [US3] Add contract test conventions section to docs/guides/testing-standards.md (API schema validation patterns)
- [ ] T035 [US3] Add contract test error handling section to testing-standards.md (standard error payload format validation)
- [ ] T036 [US3] Add contract test versioning guidance to testing-standards.md (how to handle API version changes)

### Implementation for User Story 3

- [ ] T037 [US3] Create tests/contracts/test_public_api_contract.py with @pytest.mark.contract marker
- [ ] T038 [P] [US3] Implement test_get_dataset_response_schema in test_public_api_contract.py (validates required fields and types for /api/v1/datasets/{id}/)
- [ ] T039 [P] [US3] Implement test_get_dataset_list_response_schema in test_public_api_contract.py (validates list endpoint response structure)
- [ ] T040 [P] [US3] Implement test_unauthorized_request_error_contract in test_public_api_contract.py (validates HTTP 401 error payload format)
- [ ] T041 [P] [US3] Implement test_nullable_field_explicit_null in test_public_api_contract.py (validates nullable fields return explicit null, not omitted)
- [ ] T042 [US3] Implement test_pagination_contract in test_public_api_contract.py (validates pagination metadata fields)

**Checkpoint**: Contract tests protect external API consumers from breaking changes

---

## Phase 6: User Story 4 - Feature Developer Tests Schema Mapping (Priority: P2)

**Goal**: Validate accessor paths documented in docs/ghfdb_fields.md correctly retrieve GHFDB field values

**Independent Test**: Run schema mapping tests, verify 100% of documented accessor paths work

### Documentation for User Story 4

- [ ] T043 [US4] Add schema mapping test conventions section to docs/guides/testing-standards.md (accessor path validation patterns)
- [ ] T044 [US4] Add derived field testing guidance to testing-standards.md (quality score calculation test patterns with reference values)

### Implementation for User Story 4

- [ ] T045 [US4] Create tests/test_ghfdb/test_schema_mapping.py with database-dependent tests
- [ ] T046 [P] [US4] Implement test_ghfdb_field_site_name_accessor_path in test_schema_mapping.py (HeatFlowSite.name)
- [ ] T047 [P] [US4] Implement test_ghfdb_field_coordinates_accessor_path in test_schema_mapping.py (HeatFlowSite.location.point, validates lat/lon within 0.0001)
- [ ] T048 [P] [US4] Implement test_ghfdb_field_depth_interval_accessor_path in test_schema_mapping.py (HeatFlowInterval depth fields)
- [ ] T049 [P] [US4] Implement test_ghfdb_field_heat_flow_value_accessor_path in test_schema_mapping.py (SurfaceHeatFlow.value)
- [ ] T050 [P] [US4] Implement test_ghfdb_field_thermal_conductivity_accessor_path in test_schema_mapping.py (IntervalConductivity.value)
- [ ] T051 [US4] Expand test_schema_mapping.py with tests for remaining GHFDB fields from docs/ghfdb_fields.md (incremental, target 10-15 critical fields initially)
- [ ] T052 [P] [US4] Implement test_u_score_calculation_reference_case in tests/test_heat_flow/test_quality_scores.py (known input/output from Fuchs et al. 2023)
- [ ] T053 [P] [US4] Implement test_m_score_calculation_reference_case in tests/test_heat_flow/test_quality_scores.py (known input/output from literature)

**Checkpoint**: Schema mapping tests validate all documented accessor paths and quality score calculations

---

## Phase 7: User Story 5 - Release Manager Validates Round-Trip Integrity (Priority: P3)

**Goal**: Validate export → re-import cycle preserves data within documented lossiness rules

**Independent Test**: Run round-trip tests, verify zero mandatory field differences with acceptable lossiness documented

### Documentation for User Story 5

- [ ] T054 [US5] Add acceptable lossiness rules section to docs/guides/testing-standards.md (whitespace normalization, field order, derived fields)
- [ ] T055 [US5] Add round-trip test patterns section to testing-standards.md (equivalence assertion examples)
- [ ] T056 [US5] Document unacceptable lossiness (missing mandatory fields, value corruption) in testing-standards.md

### Implementation for User Story 5

- [ ] T057 [US5] Create tests/test_ghfdb/test_round_trip_integrity.py with @pytest.mark.integration marker
- [ ] T058 [US5] Implement test_round_trip_mandatory_fields_preserved in test_round_trip_integrity.py (imports round_trip_reference.xlsx, exports, re-imports, asserts equivalence)
- [ ] T059 [US5] Implement assert_site_name_equivalent helper function in test_round_trip_integrity.py (whitespace normalization tolerance)
- [ ] T060 [US5] Implement assert_coordinates_equivalent helper function in test_round_trip_integrity.py (0.0001 precision tolerance)
- [ ] T061 [US5] Implement assert_heat_flow_equivalent helper function in test_round_trip_integrity.py (numeric precision + unit normalization)
- [ ] T062 [US5] Implement test_round_trip_optional_fields_lossiness in test_round_trip_integrity.py (documents acceptable optional field transformations)
- [ ] T063 [US5] Implement test_round_trip_derived_fields_recalculation in test_round_trip_integrity.py (quality scores may differ, documents as acceptable)
- [ ] T064 [US5] Add detailed difference reporting to round-trip tests (field name, record ID, expected vs actual on failure)

**Checkpoint**: Round-trip integrity validated with documented lossiness rules

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final documentation, CI configuration, and validation

- [ ] T065 [P] Complete docs/guides/testing-standards.md with fixture guide section (available fixtures, update process)
- [ ] T066 [P] Add "Running tests" section to testing-standards.md (pytest commands for each layer, coverage reporting)
- [ ] T067 [P] Add test markers reference table to testing-standards.md (integration, contract, slow, external, django_db)
- [ ] T068 Create symlinks from fixtures/ to tests/test_ghfdb/data/ for shared fixture files (minimal_ghfdb_import.xlsx, invalid_ghfdb_import.xlsx, round_trip_reference.xlsx)
- [ ] T069 Update CI workflow configuration (GitHub Actions) to run unit tests on every push with coverage check
- [ ] T070 Update CI workflow to run integration tests on pull requests
- [ ] T071 Update CI workflow to run contract tests before merge to main branch
- [ ] T072 Configure CI to fail when pytest-cov reports <80% coverage for modified files
- [ ] T073 Validate all tests execute successfully in CI environment (run full test suite)
- [ ] T074 Validate unit test suite completes in <30 seconds (measure and optimize if needed)
- [ ] T075 Validate integration test suite completes in <2 minutes with minimal fixtures (measure and optimize if needed)
- [ ] T076 Update tests/README.md with quick start guide referencing testing-standards.md
- [ ] T077 Review and update fixture README.md with fixture validation process (how to detect outdated fixtures)
- [ ] T078 Code review of all test files for consistency with documented conventions
- [ ] T079 Run full test suite with all markers to verify complete coverage of success criteria

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion (T001-T005) - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion (T006-T014)
  - User Story 1 (P1): Can start after Foundational
  - User Story 2 (P1): Can start after Foundational
  - User Story 3 (P2): Can start after Foundational (independent of US1/US2)
  - User Story 4 (P2): Can start after Foundational (benefits from US1 conventions but not blocking)
  - User Story 5 (P3): Can start after Foundational (should wait for US2 import/export tests to exist)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after T006-T014 (fixtures and conftest) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after T006-T014 (fixtures and conftest) - Uses fixtures created in Foundational phase
- **User Story 3 (P2)**: Can start after T006-T014 (fixtures for API data) - Independent of US1/US2 but may benefit from US1 documentation
- **User Story 4 (P2)**: Can start after T006-T014 (minimal fixture for mapping tests) - Independent but should follow US1 conventions
- **User Story 5 (P3)**: Can start after T006-T014 (round-trip fixture) - Logically depends on US2 having import/export tests, but technically independent

### Within Each User Story

**User Story 1 (Unit Test Conventions)**:

- Documentation tasks (T015-T019) can run in parallel
- Example tests (T020-T022) depend on T015 (testing-standards.md exists) but can run in parallel with each other
- Suggested order: T015 first, then T016-T019 and T020-T022 in parallel

**User Story 2 (Integration Tests)**:

- Documentation (T023-T025) can run in parallel
- Test files (T026, T029) can be created in parallel
- Test implementations within each file should follow workflow order (import → review → approval → export)
- T027-T028 (import tests) can run in parallel
- T030-T031 (review tests) can run in parallel
- T032-T033 depend on earlier tests existing for context

**User Story 3 (Contract Tests)**:

- Documentation (T034-T036) can run in parallel
- T037 (create test file) must complete before test implementations
- T038-T041 (schema validation tests) can run in parallel
- T042 (pagination) independent

**User Story 4 (Schema Mapping)**:

- Documentation (T043-T044) can run in parallel
- T045 (create test file) must complete first
- T046-T050 (accessor path tests) can run in parallel
- T051 is incremental expansion over time
- T052-T053 (quality scores) can run in parallel, independent of accessor tests

**User Story 5 (Round-Trip)**:

- Documentation (T054-T056) can run in parallel
- T057 (create test file) must complete first
- T058 (main round-trip test) should be implemented first
- T059-T061 (helper functions) can be implemented in parallel as needed by T058
- T062-T064 (additional lossiness tests) can run in parallel after helpers exist

### Parallel Opportunities

**Setup Phase**: T002-T004 (pyproject.toml updates) can run in parallel if coordinated

**Foundational Phase**:

- T006-T010 (fixture creation) can run in parallel - different files
- T012-T014 (conftest fixtures) can run in parallel - different fixture loaders

**User Story 1**:

- T016-T019 (documentation sections) can run in parallel
- T020-T022 (example tests) can run in parallel

**User Story 2**:

- T023-T025 (documentation) can run in parallel
- T026 and T029 (test file creation) can run in parallel
- T027-T028 can run in parallel (different test functions)
- T030-T031 can run in parallel (different test functions)

**User Story 3**:

- T034-T036 (documentation) can run in parallel
- T038-T041 (schema tests) can run in parallel after T037

**User Story 4**:

- T043-T044 (documentation) can run in parallel
- T046-T050 (accessor tests) can run in parallel after T045
- T052-T053 (quality score tests) can run in parallel

**User Story 5**:

- T054-T056 (documentation) can run in parallel
- T059-T061 (helper functions) can be developed in parallel

**Polish Phase**:

- T065-T067 (documentation completion) can run in parallel
- T069-T071 (CI workflow sections) can run in parallel

---

## Parallel Example: User Story 2 Integration Tests

```bash
# After Foundational phase complete, launch User Story 2 work:

# Team Member 1: Documentation
Task: "Add integration test conventions section to docs/guides/testing-standards.md"
Task: "Add integration test fixture usage guide to testing-standards.md"
Task: "Add integration test assertion strategies to testing-standards.md"

# Team Member 2: Import workflow tests
Task: "Create tests/test_ghfdb/test_import_workflow_integration.py"
Task: "Implement test_import_minimal_dataset_happy_path"
Task: "Implement test_import_invalid_dataset_raises_validation_errors"
Task: "Implement test_export_without_approval_fails"

# Team Member 3: Review workflow tests
Task: "Create tests/test_review/test_review_workflow_integration.py"
Task: "Implement test_submit_for_review_state_transition"
Task: "Implement test_approve_for_publication_requires_admin"

# Team Member 4: End-to-end test
Task: "Implement test_full_workflow_import_to_export" (depends on T026-T027)
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. **Complete Phase 1**: Setup (T001-T005) - ~2-4 hours
2. **Complete Phase 2**: Foundational (T006-T014) - ~1-2 days (fixture creation is time-intensive)
3. **Complete Phase 3**: User Story 1 (T015-T022) - ~1-2 days
4. **Complete Phase 4**: User Story 2 (T023-T033) - ~2-3 days
5. **STOP and VALIDATE**: Run unit and integration test suites, verify <30s and <2min timing
6. **Deploy conventions**: Update CONTRIBUTING.md referencing testing-standards.md

**MVP Deliverable**: Developers can write unit tests following conventions, QA can validate import-to-export workflow with integration tests, fixtures exist for core workflows.

### Incremental Delivery

1. **Setup + Foundational** (Phases 1-2) → Foundation ready (~3-4 days)
2. **Add User Story 1** → Unit test conventions documented and validated (~2-3 days cumulative)
3. **Add User Story 2** → Integration tests working (~5-6 days cumulative) - **MVP HERE**
4. **Add User Story 3** → Contract tests protecting API (~7-8 days cumulative)
5. **Add User Story 4** → Schema mapping validated (~9-10 days cumulative)
6. **Add User Story 5** → Round-trip integrity tested (~11-12 days cumulative)
7. **Polish + CI** (Phase 8) → Complete, enforceable in CI (~13-15 days cumulative)

Each story adds value without breaking previous stories. Stop at any checkpoint for early value delivery.

### Parallel Team Strategy

With 3-4 developers after Foundational phase completes:

1. **Team completes Setup + Foundational together** (Phases 1-2)
2. **Once Foundational is done** (T006-T014 complete):
   - **Developer A**: User Story 1 (Unit test conventions + docs)
   - **Developer B**: User Story 2 (Integration tests for import/review)
   - **Developer C**: User Story 3 (Contract tests for API)
   - **Developer D**: User Story 4 (Schema mapping tests)
3. **User Story 5** starts after US2 complete (Developer B transitions)
4. **Phase 8** (Polish) after all stories complete (whole team)

**Timeline with parallel work**: ~7-10 days vs ~13-15 days sequential

---

## Notes

- **[P] marker**: Tasks operating on different files with no dependencies can run in parallel
- **[Story] labels**: Enable tracking which tasks belong to each user story for independent delivery
- **Fixture creation (Phase 2)** is the most time-intensive part (~1-2 days) - fixtures must have realistic, valid data representing diverse scenarios
- **Test execution timing** (SC-002, SC-003) should be validated continuously during implementation, optimizing fixture loading and database setup if needed
- **Schema mapping coverage** (T051) is incremental - start with 10-15 critical fields, expand over time as schedule allows
- **CI configuration** (Phase 8) can begin early as tests are written, with iterative updates as new test categories are added
- **Constitution Principle VII** requires tests be written FIRST - each test should FAIL before implementation
- **Commit strategy**: Commit after completing each task or logical group (e.g., all fixtures, all unit test docs)
- **Stop at any checkpoint** to validate story independently before proceeding

---

## Total Task Count

- **Phase 1 (Setup)**: 5 tasks
- **Phase 2 (Foundational)**: 9 tasks
- **Phase 3 (User Story 1)**: 8 tasks
- **Phase 4 (User Story 2)**: 11 tasks
- **Phase 5 (User Story 3)**: 9 tasks
- **Phase 6 (User Story 4)**: 9 tasks
- **Phase 7 (User Story 5)**: 8 tasks
- **Phase 8 (Polish)**: 15 tasks

**Total: 74 tasks**

**MVP scope (US1 + US2 only)**: 33 tasks (Setup + Foundational + US1 + US2)
**Full implementation**: 74 tasks
