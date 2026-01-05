# Implementation Plan: Testing Infrastructure & Conventions

**Branch**: `002-testing-infrastructure` | **Date**: 2026-01-05 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-testing-infrastructure/spec.md`

## Summary

This feature establishes comprehensive testing infrastructure and conventions for the Global Heat Flow Database portal to enforce Constitution Principle VII (Test-Driven Development). It defines three test layers (unit, integration, contract), naming conventions, pytest marker categorization, five minimum fixture datasets for core workflows, schema mapping test requirements, round-trip integrity validation, and CI configuration. The primary goal is to make future feature specs enforceable by providing unambiguous references to test locations, fixtures, and validation criteria.

## Technical Context

**Language/Version**: Python 3.13 (as specified in pyproject.toml)
**Primary Dependencies**: pytest, pytest-django, pytest-cov, Django 5.0, FairDM framework
**Storage**: Django test database with transaction rollback for unit/integration tests; static fixture files (Excel, JSON) in tests/ subdirectories
**Testing**: pytest with custom markers (integration, contract, slow, external, django_db)
**Target Platform**: Linux server (development and CI), Windows developer workstations
**Project Type**: Django web application
**Performance Goals**: Unit test suite <30 seconds, integration test suite <2 minutes, 80% coverage threshold for modified files
**Constraints**: Tests must be runnable on developer laptops without external service dependencies (use mocking); fixtures must remain under 100KB each for fast loading
**Scale/Scope**: ~100-200 tests initially across 3 layers; fixture datasets covering 5-10 heat flow sites each; schema mapping tests for ~50-80 GHFDB fields documented in docs/ghfdb_fields.md

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**I. Schema Fidelity**: N/A - This feature documents how to test schema fidelity but doesn't modify schema mappings. Schema mapping tests (User Story 4) will validate docs/ghfdb_fields.md accessor paths.

**II. FairDM Integration**: PASS - Uses FairDM test patterns (factory fixtures, FairDM model testing). No custom test infrastructure conflicts with FairDM expectations.

**III. Schema Transparency**: PASS - Schema mapping tests (FR-020 to FR-023) explicitly test accessor paths documented in docs/ghfdb_fields.md, ensuring transparency requirements are testable.

**IV. Open Science & Data Quality**: PASS - Contract tests (User Story 3) validate API openness; quality score calculation tests (FR-023, User Story 4) validate quality standards are correctly implemented.

**V. Community Collaboration**: N/A - Testing infrastructure is internal development tooling, not directly user-facing.

**VI. Provenance & Attribution**: PASS - Integration tests (User Story 2) validate review workflow state transitions including provenance metadata capture (FR-017, FR-018 fixtures include provenance).

**VII. Test-Driven Development**: PASS - This feature IS the implementation of Constitution Principle VII. Defines pytest-based TDD workflow, coverage thresholds, and test-first conventions.

**VIII. Documentation Standards**: PASS - Includes documentation requirements (FR-031 to FR-033) for testing guide, lossiness rules, and contract test patterns.

## Project Structure

### Documentation (this feature)

```text
specs/002-testing-infrastructure/
├── spec.md                  # Feature specification (complete)
├── plan.md                  # This file (implementation plan)
├── checklists/
│   └── requirements.md      # Quality validation checklist (complete)
└── tasks.md                 # Task breakdown (to be created by /speckit.tasks)
```

### Source Code (repository root)

```text
# Django application structure (existing - will be extended)
tests/
├── __init__.py                          # Existing
├── conftest.py                          # Existing - will be extended with new fixtures
├── README.md                            # Existing - will be updated with new conventions
│
├── test_heat_flow/                      # Existing unit tests - will follow new conventions
│   ├── __init__.py
│   ├── test_factories.py
│   ├── test_heat_flow_site_factory.py
│   ├── test_models.py
│   └── test_views.py
│
├── test_ghfdb/                          # Existing unit tests - will be extended
│   ├── __init__.py
│   ├── test_importer.py
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_import_workflow_integration.py    # NEW - User Story 2
│   ├── test_schema_mapping.py                 # NEW - User Story 4
│   ├── test_round_trip_integrity.py           # NEW - User Story 5
│   └── data/                            # Existing test data directory
│       ├── importer_fail.xlsx           # Existing
│       ├── importer_fail_single_row.xlsx # Existing
│       ├── importer_success.xlsx         # Existing
│       ├── minimal_ghfdb_import.xlsx     # NEW - FR-015
│       ├── invalid_ghfdb_import.xlsx     # NEW - FR-016
│       └── round_trip_reference.xlsx     # NEW - FR-019
│
├── test_review/                         # Existing - will be extended
│   ├── __init__.py
│   ├── test_models.py
│   └── test_review_workflow_integration.py    # NEW - User Story 2
│
└── contracts/                           # NEW - User Story 3
    ├── __init__.py
    └── test_public_api_contract.py      # NEW - FR-004

# Fixtures directory (existing - will be extended)
fixtures/
├── minimal_ghfdb_import.xlsx            # NEW - FR-015 (symlink or copy from tests/test_ghfdb/data/)
├── invalid_ghfdb_import.xlsx            # NEW - FR-016 (symlink or copy from tests/test_ghfdb/data/)
├── review_submission_dataset.json       # NEW - FR-017
├── admin_approval_dataset.json          # NEW - FR-018
└── round_trip_reference.xlsx            # NEW - FR-019 (symlink or copy from tests/test_ghfdb/data/)

# Configuration (existing - will be updated)
pyproject.toml                           # Existing - will add pytest markers and coverage config

# Documentation (to be created)
docs/
└── guides/
    └── testing-standards.md             # NEW - FR-031
```

**Structure Decision**: Django monorepo with tests/ organized by app (test_<app_name>/) plus a new contracts/ directory for API contract tests. Fixture datasets live in both tests/test_<app>/data/ (for test-specific fixtures) and root fixtures/ directory (for shared fixtures referenced by multiple test suites). This follows Django and pytest conventions while supporting the three-layer test architecture defined in the spec.

## Implementation Approach

### Phase 1: Setup & Configuration (User Story 1 Foundation)

**Purpose**: Establish pytest configuration, markers, and directory structure for all test layers.

**Key Decisions**:

1. **pytest marker registration**: Add to `pyproject.toml` under `[tool.pytest.ini_options]`:

   ```toml
   markers = [
       "integration: Integration tests requiring full Django stack and database",
       "contract: Contract tests validating API response schemas",
       "slow: Tests taking >5 seconds (excluded from default run)",
       "external: Tests requiring external services (skip when unavailable)",
       "django_db: Tests requiring database access"
   ]
   ```

2. **Test discovery configuration**: Configure pytest to default to unit tests only:

   ```toml
   testpaths = ["tests"]
   python_files = ["test_*.py"]
   python_classes = ["Test*"]
   python_functions = ["test_*"]
   addopts = [
       "-v",
       "--tb=short",
       "--strict-markers",
       "-m", "not integration and not contract and not slow and not external"
   ]
   ```

3. **Coverage configuration**: Add pytest-cov settings:

   ```toml
   [tool.coverage.run]
   source = ["project"]
   omit = ["*/migrations/*", "*/tests/*", "*/conftest.py"]

   [tool.coverage.report]
   fail_under = 80
   show_missing = true
   skip_covered = false
   ```

4. **Directory creation**: Create `tests/contracts/` directory with `__init__.py`.

**Deliverable**: Updated `pyproject.toml`, `tests/contracts/` directory, and `tests/README.md` with marker usage guide.

---

### Phase 2: Fixture Datasets (User Stories 2, 4, 5 Foundation)

**Purpose**: Create minimal, reusable fixture datasets that represent core workflow states and provide known test data.

**Key Decisions**:

1. **Fixture format choices**:
   - Import/export fixtures: Excel (.xlsx) format matching GHFDB template structure
   - Workflow state fixtures: Django JSON fixtures with FairDM model instances
   - Rationale: Excel for import fidelity testing; JSON for workflow state reproducibility

2. **Fixture content strategy**:
   - `minimal_ghfdb_import.xlsx`: 5 heat flow sites with complete mandatory fields, representing a clean happy-path import (sites from different continents, various depth intervals)
   - `invalid_ghfdb_import.xlsx`: 5 rows with specific validation errors (missing Site_Name, invalid latitude >90, negative heat flow value, empty mandatory field, out-of-range depth)
   - `round_trip_reference.xlsx`: 10 heat flow sites covering all GHFDB field types including optional fields, edge cases (null optionals, max string lengths, boundary numeric values)
   - `review_submission_dataset.json`: Django fixture with Dataset instance in "pending review" state, complete provenance (DOI, contributors, publication metadata)
   - `admin_approval_dataset.json`: Django fixture with Dataset instance in "reviewed" state ready for publication approval

3. **Fixture validation**: Each fixture must be validated against current schema before inclusion (automated check in CI).

4. **Fixture maintenance**: Fixtures are versioned with the codebase and updated whenever schema changes require it.

**Deliverable**: 5 fixture files (3 Excel, 2 JSON) in appropriate locations, with fixture README documenting purpose and update process.

---

### Phase 3: Unit Test Conventions Documentation (User Story 1)

**Purpose**: Document conventions for writing fast, isolated unit tests with examples.

**Key Decisions**:

1. **Test organization pattern**:
   - File: `tests/test_<app>/test_<module>.py` mirrors `project/<app>/<module>.py`
   - Class: `class Test<FeatureName>` groups related tests
   - Function: `def test_<action>_<condition>_<expected_result>()`
   - Example: `tests/test_heat_flow/test_models.py::TestHeatFlowValidation::test_validate_temperature_negative_value_raises_error`

2. **Fixture naming pattern**:
   - `@pytest.fixture` functions use lowercase_with_underscores
   - Fixture names describe what they provide: `minimal_dataset`, `invalid_coordinates`, `mock_doi_service`
   - Scope explicitly declared: `scope="function"` (default), `scope="module"`, `scope="session"`

3. **Database access policy**:
   - Unit tests AVOID database unless absolutely necessary (use factories, mocks)
   - When database required, mark with `@pytest.mark.django_db` and document reason
   - Use `pytest.mark.django_db(transaction=True)` for tests requiring transaction rollback

4. **Parametrized test pattern**:

   ```python
   @pytest.mark.parametrize("latitude,expected_error", [
       (-91, "Latitude must be >= -90"),
       (91, "Latitude must be <= 90"),
       (None, "Latitude is required"),
   ])
   def test_validate_coordinates_invalid_latitude_raises_error(latitude, expected_error):
       # test implementation
   ```

**Deliverable**: `docs/guides/testing-standards.md` section on unit test conventions with 5-10 code examples.

---

### Phase 4: Integration Test Infrastructure (User Story 2)

**Purpose**: Enable full-stack testing of complete workflows (import → review → approval → export) using fixtures.

**Key Decisions**:

1. **Integration test location**: `tests/test_<app>/test_<workflow>_integration.py`
   - Example: `tests/test_ghfdb/test_import_workflow_integration.py`
   - Example: `tests/test_review/test_review_workflow_integration.py`

2. **Marker usage**: All integration tests marked with `@pytest.mark.integration`

3. **Database strategy**: Use Django test database with transaction rollback after each test (pytest-django default)

4. **Workflow test structure**:

   ```python
   @pytest.mark.integration
   @pytest.mark.django_db
   def test_import_to_export_happy_path(minimal_ghfdb_import_fixture):
       # 1. Import phase
       dataset = import_ghfdb_template(minimal_ghfdb_import_fixture)
       assert dataset.state == "imported"

       # 2. Review phase
       submit_for_review(dataset)
       assert dataset.state == "under_review"

       # 3. Approval phase
       approve_for_publication(dataset, admin_user)
       assert dataset.state == "approved"

       # 4. Export phase
       export_file = export_to_ihfc_format(dataset)
       assert_export_contains_all_sites(export_file, expected_count=5)
   ```

5. **Assertion strategy**: Each workflow stage has specific assertions validating state transitions, data preservation, and authorization checks.

**Deliverable**: Integration test files for import, review, and export workflows; `docs/guides/testing-standards.md` section on integration testing with workflow examples.

---

### Phase 5: Contract Test Infrastructure (User Story 3)

**Purpose**: Validate public API response schemas remain backward-compatible across releases.

**Key Decisions**:

1. **Contract test tool**: Use pytest + requests + jsonschema (or pydantic for schema validation)

2. **Test organization**: `tests/contracts/test_<api_area>_contract.py`
   - Example: `tests/contracts/test_public_api_contract.py`

3. **Schema definition source**: Reference OpenAPI schema or inline JSON Schema definitions (decide based on P4-01 API contract spec availability)

4. **Contract test structure**:

   ```python
   @pytest.mark.contract
   def test_get_dataset_response_schema():
       response = api_client.get("/api/v1/datasets/123/")
       assert response.status_code == 200

       # Validate required fields present with correct types
       data = response.json()
       assert "id" in data and isinstance(data["id"], str)
       assert "name" in data and isinstance(data["name"], str)
       assert "doi" in data and (data["doi"] is None or isinstance(data["doi"], str))
       assert "publication_date" in data
       assert "contributors" in data and isinstance(data["contributors"], list)
   ```

5. **Error contract validation**: Test error responses match standard payload format `{"error": "...", "detail": "..."}`

**Deliverable**: Contract test file for public API; `docs/guides/testing-standards.md` section on contract testing with schema validation examples.

---

### Phase 6: Schema Mapping Tests (User Story 4)

**Purpose**: Validate accessor paths documented in `docs/ghfdb_fields.md` correctly retrieve GHFDB field values from normalized database.

**Key Decisions**:

1. **Test data source**: Use `minimal_ghfdb_import.xlsx` fixture with known field values

2. **Mapping test structure**:

   ```python
   @pytest.mark.django_db
   def test_ghfdb_field_site_name_accessor_path():
       # Import fixture with known Site_Name = "Test Borehole 1"
       dataset = import_fixture("minimal_ghfdb_import.xlsx")
       site = HeatFlowSite.objects.filter(dataset=dataset).first()

       # Validate accessor path from docs/ghfdb_fields.md
       assert site.name == "Test Borehole 1"

   @pytest.mark.django_db
   def test_ghfdb_field_coordinates_accessor_path():
       dataset = import_fixture("minimal_ghfdb_import.xlsx")
       site = HeatFlowSite.objects.filter(dataset=dataset).first()

       # Accessor: HeatFlowSite.location.point
       point = site.location.point
       assert abs(point.x - 13.405) < 0.0001  # Longitude
       assert abs(point.y - 52.52) < 0.0001   # Latitude
   ```

3. **Derived field testing**: Quality score calculations tested separately with known input/output pairs from Fuchs et al. (2023):

   ```python
   def test_u_score_calculation_reference_case():
       # Known inputs from literature
       measurement = create_measurement(
           thermal_conductivity=2.5,  # W/m/K
           depth_confidence="high",
           # ... other U-score inputs
       )

       expected_u_score = 8  # From Fuchs et al. (2023) Table X
       calculated_u_score = measurement.calculate_u_score()
       assert calculated_u_score == expected_u_score
   ```

4. **Test generation strategy**: Initially handwrite tests for ~10-15 most critical GHFDB fields; expand coverage incrementally to all ~50-80 fields over time.

**Deliverable**: `tests/test_ghfdb/test_schema_mapping.py` with accessor path validation tests; quality score calculation test in `tests/test_heat_flow/test_models.py`.

---

### Phase 7: Round-Trip Integrity Tests (User Story 5)

**Purpose**: Validate export → re-import cycle preserves data within documented lossiness rules.

**Key Decisions**:

1. **Test fixture**: Use `round_trip_reference.xlsx` containing diverse field types and edge cases

2. **Equivalence rules** (documented in tests and `docs/guides/testing-standards.md`):
   - **Mandatory fields**: Exact match required (string equality, numeric precision within 0.0001)
   - **Acceptable lossiness**:
     - Whitespace normalization (leading/trailing trim, multiple spaces → single space)
     - Field order changes (rows/columns may be reordered if semantically equivalent)
     - Derived fields recalculated (quality scores may change if calculation logic improves)
   - **Unacceptable lossiness**: Missing mandatory fields, value corruption, incorrect relationships

3. **Round-trip test structure**:

   ```python
   @pytest.mark.integration
   @pytest.mark.django_db
   def test_round_trip_mandatory_fields_preserved():
       # Import reference dataset
       original_dataset = import_fixture("round_trip_reference.xlsx")
       original_sites = HeatFlowSite.objects.filter(dataset=original_dataset)

       # Export to IHFC format
       export_file = export_to_ihfc_format(original_dataset)

       # Re-import exported file
       reimported_dataset = import_ghfdb_template(export_file)
       reimported_sites = HeatFlowSite.objects.filter(dataset=reimported_dataset)

       # Assert mandatory field preservation
       assert original_sites.count() == reimported_sites.count()
       for orig, reimp in zip(original_sites, reimported_sites):
           assert_site_name_equivalent(orig.name, reimp.name)  # Whitespace normalized
           assert_coordinates_equivalent(orig.location, reimp.location, tolerance=0.0001)
           assert_heat_flow_equivalent(orig.measurements, reimp.measurements, tolerance=0.0001)
   ```

4. **Difference reporting**: When equivalence fails, report specific field, record ID, expected value, actual value

**Deliverable**: `tests/test_ghfdb/test_round_trip_integrity.py` with equivalence rule tests; acceptable lossiness documentation in `docs/guides/testing-standards.md`.

---

### Phase 8: Documentation & CI Integration (Cross-Cutting)

**Purpose**: Provide developer guide and enforce test coverage in CI.

**Key Decisions**:

1. **Testing guide structure** (`docs/guides/testing-standards.md`):
   - Introduction (test pyramid, TDD workflow)
   - Unit test conventions (organization, naming, database policy, examples)
   - Integration test conventions (workflow testing, fixture usage, examples)
   - Contract test conventions (API schema validation, error contracts, examples)
   - Fixture guide (available fixtures, update process)
   - Running tests (pytest commands for each layer, coverage reporting)
   - Acceptable lossiness rules for round-trip tests
   - Test markers reference

2. **CI configuration** (GitHub Actions or similar):

   ```yaml
   # Fast feedback: Run unit tests on every push
   - name: Run unit tests
     run: poetry run pytest -v --cov=project --cov-report=term --cov-fail-under=80

   # Comprehensive: Run integration tests on PR
   - name: Run integration tests
     run: poetry run pytest -m integration -v

   # Gated: Run contract tests before merge to main
   - name: Run contract tests
     run: poetry run pytest -m contract -v
   ```

3. **Coverage enforcement**: pytest-cov configured to fail build when coverage <80% for modified files (not entire codebase, to allow incremental adoption)

**Deliverable**: Complete `docs/guides/testing-standards.md`; CI workflow file with test execution and coverage enforcement; updated `tests/README.md` with quick start guide.

---

## Complexity Tracking

> **No constitutional violations identified** - All requirements align with Constitution principles, particularly Principle VII (Test-Driven Development). This feature implements rather than violates the constitution.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

---

## Risk Assessment

**Low Risk**:

- Test infrastructure is additive (doesn't modify production code)
- Fixture creation is straightforward (static data files)
- pytest marker configuration is standard practice

**Medium Risk**:

- Schema mapping tests depend on `docs/ghfdb_fields.md` accuracy (mitigation: validate accessor paths during fixture creation)
- Integration test timing (<2 minutes) may require optimization if fixture loading is slow (mitigation: use minimal fixtures, lazy loading)
- Round-trip lossiness rules may be incomplete initially (mitigation: document discovered lossiness incrementally, don't block on perfection)

**High Risk**:

- None identified

---

## Acceptance Criteria Mapping

| Success Criterion | Implementation Phase | Validation Method |
|-------------------|----------------------|-------------------|
| SC-001: Unambiguous test layer references | Phase 1 (Setup), Phase 8 (Docs) | Review of `tests/README.md` and `docs/guides/testing-standards.md` |
| SC-002: Unit tests <30 seconds | Phase 3 (Unit test conventions) | CI timing measurement |
| SC-003: Integration tests <2 minutes | Phase 4 (Integration infrastructure) | CI timing measurement with minimal fixtures |
| SC-004: 100% accessor path coverage | Phase 6 (Schema mapping tests) | Test count matches `docs/ghfdb_fields.md` field count |
| SC-005: Round-trip zero mandatory diffs | Phase 7 (Round-trip tests) | Automated assertion in test suite |
| SC-006: Contract tests validate API schema | Phase 5 (Contract infrastructure) | Schema validation assertions pass |
| SC-007: CI fails <80% coverage | Phase 8 (CI integration) | pytest-cov configuration + CI workflow |
| SC-008: Actionable error messages | All phases | Manual review of test failure output during development |

---

## Next Steps

1. **Execute `/speckit.tasks`**: Generate detailed task breakdown organized by user story priority
2. **Review plan with team**: Validate fixture content strategy and lossiness rules with QA and senior developers
3. **Begin Phase 1**: Create feature branch, update `pyproject.toml` with pytest markers
4. **TDD workflow**: Write failing tests before implementing each phase (per Constitution Principle VII)
