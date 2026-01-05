# Feature Specification: Testing Infrastructure & Conventions

**Feature Branch**: `002-testing-infrastructure`
**Created**: 2026-01-05
**Status**: Draft
**Input**: User description: "Create a feature spec defining the testing strategy, test layers, and minimum fixtures required to make later specs enforceable. The spec should define test layers (unit/integration/contract) and where they live under tests/, naming conventions for test files and test functions, minimal fixture datasets for import, review submission, admin approval, and export workflows, and how to write tests for schema mapping and round-trip integrity."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Feature Developer Writes Unit Tests (Priority: P1)

A feature developer is implementing a new data validation rule for heat flow measurements. They need to write focused unit tests that validate the business logic in isolation, without dependencies on the database, external services, or the full Django application stack. The developer should be able to run these tests quickly (under 5 seconds for a typical module) during development to get immediate feedback.

**Why this priority**: Unit tests are the foundation of the testing pyramid and provide the fastest feedback loop. Without clear conventions for unit testing, developers will either skip tests or write slow integration tests for everything, slowing down the development cycle and reducing test coverage.

**Independent Test**: Can be fully tested by creating a sample unit test module following the conventions, running it with pytest, and verifying it executes in under 5 seconds with clear pass/fail output.

**Acceptance Scenarios**:

1. **Given** a new model method that validates temperature ranges, **When** the developer writes unit tests in `tests/test_heat_flow/test_models.py` using factory-generated instances, **Then** the tests execute without database access and provide clear assertion failures for invalid inputs.
2. **Given** a utility function that normalizes geographic coordinates, **When** the developer writes parametrized unit tests with edge cases (null values, out-of-range values, boundary values), **Then** all test cases execute in parallel and report which specific parameter set failed.
3. **Given** a new quality score calculation function, **When** the developer writes unit tests with known input/output pairs from published literature, **Then** the test output shows whether the calculated score matches the expected value with appropriate precision.

---

### User Story 2 - QA Engineer Validates Import-to-Export Workflow (Priority: P1)

A QA engineer needs to validate that the complete data lifecycle (import → review → approval → export) works correctly for a representative dataset. They need an integration test that exercises the full stack including database transactions, file I/O, Django views, and background tasks, using a minimal but realistic fixture dataset. The test should complete in under 2 minutes and produce a detailed log showing which workflow step succeeded or failed.

**Why this priority**: Integration tests validate that components work together correctly, catching interface mismatches and configuration errors that unit tests miss. The import-to-export workflow is the core value proposition of the portal, so having a reliable integration test is essential for preventing regressions.

**Independent Test**: Can be fully tested by running the integration test suite with `pytest -m integration`, verifying it uses the minimal fixture dataset, and confirming it exercises all major workflow transitions with database rollback after completion.

**Acceptance Scenarios**:

1. **Given** a minimal GHFDB Excel template with 5 heat flow sites, **When** the integration test imports the template, submits it for review, approves it as admin, and exports to IHFC format, **Then** the exported spreadsheet contains the same 5 sites with all mandatory fields preserved.
2. **Given** a dataset in "under review" state, **When** the integration test attempts to export it without admin approval, **Then** the test fails with a clear authorization error message indicating approval is required.
3. **Given** a dataset with deliberately invalid data (missing mandatory fields), **When** the integration test attempts to approve it for publication, **Then** the test fails with validation errors listing specific missing fields and their locations.

---

### User Story 3 - API Consumer Verifies Contract Stability (Priority: P2)

An external data harvester developer needs to verify that the public REST API maintains backward compatibility across portal releases. They need contract tests that validate API response schemas, field names, data types, and error formats against a documented contract, so they can detect breaking changes before deploying updates to production harvesters.

**Why this priority**: Contract tests protect external API consumers from unexpected breaking changes, enabling the portal to evolve its internals without disrupting downstream systems. While important, this is secondary to having working core functionality (P1 priorities).

**Independent Test**: Can be fully tested by running contract tests against a test API endpoint, sending requests with known parameters, and validating response structure matches the OpenAPI/JSON schema definition.

**Acceptance Scenarios**:

1. **Given** a published dataset accessible via `/api/v1/datasets/{id}/`, **When** the contract test requests the dataset, **Then** the response includes required fields (id, name, doi, publication_date, contributors) with correct data types as defined in the API schema.
2. **Given** an authenticated request to a reviewer-only endpoint, **When** the contract test uses an invalid token, **Then** the response is HTTP 401 with a standard error payload containing `{\"error\": \"Unauthorized\", \"detail\": \"...\"}`.
3. **Given** the API schema defines a field as nullable, **When** the contract test requests a dataset where that field is null, **Then** the response includes the field with explicit `null` value rather than omitting it.

---

### User Story 4 - Feature Developer Tests Schema Mapping (Priority: P2)

A developer implementing changes to the GHFDB import logic needs to verify that flat spreadsheet fields correctly map to normalized relational database tables. They need tests that validate accessor paths documented in `docs/ghfdb_fields.md` are correct and that derived fields are calculated as specified.

**Why this priority**: Schema mapping is complex due to the conceptual-to-relational impedance mismatch. Without explicit tests, mapping errors can go undetected until publication, causing data loss or corruption. This is slightly lower priority than basic integration tests because it's a subset of the import workflow.

**Independent Test**: Can be fully tested by loading a fixture with known GHFDB field values, using the documented accessor path to retrieve each field, and asserting the retrieved value matches the input.

**Acceptance Scenarios**:

1. **Given** a GHFDB spreadsheet with `Site_Name` = "Test Borehole 1", **When** the mapping test imports the spreadsheet and accesses `HeatFlowSite.name`, **Then** the accessor returns "Test Borehole 1".
2. **Given** a GHFDB spreadsheet with `Latitude_deg` = "52.5200" and `Longitude_deg` = "13.4050", **When** the mapping test accesses `HeatFlowSite.location.point`, **Then** the point coordinates match (52.52, 13.405) within 0.0001 decimal degrees.
3. **Given** a GHFDB spreadsheet with fields required for U-score calculation, **When** the mapping test calculates the quality score, **Then** the calculated U-score matches the expected value defined in Fuchs et al. (2023) Section 3.4.

---

### User Story 5 - Release Manager Validates Round-Trip Integrity (Priority: P3)

A release manager preparing a public data release needs to verify that data exported from the portal can be re-imported without loss or corruption. They need round-trip tests that import a dataset, export it to IHFC format, re-import the export, and assert equivalence under documented lossiness rules (e.g., whitespace normalization is acceptable, missing mandatory fields are not).

**Why this priority**: Round-trip integrity is crucial for data preservation and migration scenarios, but it's a higher-level validation that assumes basic import/export functionality works (P1/P2). It's primarily relevant for major releases and schema migrations.

**Independent Test**: Can be fully tested by running a round-trip test with a reference dataset, comparing the re-imported data to the original using canonical equivalence rules, and reporting any differences.

**Acceptance Scenarios**:

1. **Given** a dataset with 10 heat flow measurements, **When** the round-trip test exports to IHFC Excel format and re-imports, **Then** all 10 measurements are present with identical values for mandatory fields (site name, coordinates, heat flow value).
2. **Given** a dataset with optional fields containing leading/trailing whitespace, **When** the round-trip test exports and re-imports, **Then** whitespace is normalized but semantic content is preserved (documented as acceptable lossiness).
3. **Given** a dataset with derived fields (calculated scores), **When** the round-trip test exports and re-imports, **Then** derived fields are recalculated during import and may differ from the original export (documented as acceptable lossiness).

---

### Edge Cases

- What happens when a unit test requires database access due to model signals or complex manager methods? (Should use `pytest.mark.django_db` and document as database-dependent unit test)
- How does the system handle integration tests that depend on external services (e.g., DOI validation)? (Should mock external services or skip tests with appropriate markers when services are unavailable)
- What happens when a contract test detects a breaking API change in a pre-release branch? (Should fail CI and require explicit documentation of the breaking change before merge)
- How does the system handle fixtures that become outdated as the schema evolves? (Should have fixture validation tests that fail when fixtures no longer match current schema, triggering fixture updates)
- What happens when round-trip tests encounter acceptable vs unacceptable lossiness? (Should have explicit assertions for required field preservation and tolerance rules for acceptable transformations)

## Requirements *(mandatory)*

### Functional Requirements

#### Test Layer Organization

- **FR-001**: System MUST organize tests into three layers: unit tests (fast, isolated, no database), integration tests (full stack, database, fixtures), and contract tests (API schema validation).
- **FR-002**: Unit tests MUST live in `tests/test_<app_name>/test_<module>.py` (e.g., `tests/test_heat_flow/test_models.py`) mirroring the application structure.
- **FR-003**: Integration tests MUST live in `tests/test_<app_name>/test_<workflow>_integration.py` (e.g., `tests/test_ghfdb/test_import_workflow_integration.py`).
- **FR-004**: Contract tests MUST live in `tests/contracts/test_<api_area>_contract.py` (e.g., `tests/contracts/test_public_api_contract.py`).
- **FR-005**: Test data files MUST be organized in `tests/test_<app_name>/data/` subdirectories (e.g., `tests/test_ghfdb/data/minimal_import.xlsx`).

#### Naming Conventions

- **FR-006**: Test file names MUST follow the pattern `test_*.py` to be discoverable by pytest.
- **FR-007**: Test function names MUST be descriptive and follow the pattern `test_<action>_<condition>_<expected_result>` (e.g., `test_import_invalid_template_raises_validation_error`).
- **FR-008**: Test class names MUST follow the pattern `Test<FeatureName>` when grouping related tests (e.g., `class TestQualityScoreCalculation`).
- **FR-009**: Fixture function names MUST be lowercase with underscores describing what they provide (e.g., `@pytest.fixture def minimal_dataset():`).

#### Test Markers and Categories

- **FR-010**: Unit tests MUST NOT use database access unless marked with `@pytest.mark.django_db` and documented as database-dependent.
- **FR-011**: Integration tests MUST be marked with `@pytest.mark.integration` for selective execution.
- **FR-012**: Slow tests (>5 seconds) MUST be marked with `@pytest.mark.slow` and should not block quick development feedback loops.
- **FR-013**: Contract tests MUST be marked with `@pytest.mark.contract` and should run against both development and staging environments.
- **FR-014**: Tests requiring external services MUST be marked with `@pytest.mark.external` and should gracefully skip when services are unavailable.

#### Fixture Requirements

- **FR-015**: System MUST provide a minimal fixture dataset (`fixtures/minimal_ghfdb_import.xlsx`) containing 5 heat flow sites with complete mandatory fields for testing happy-path import workflows.
- **FR-016**: System MUST provide an invalid fixture dataset (`fixtures/invalid_ghfdb_import.xlsx`) containing various validation errors (missing mandatory fields, invalid coordinates, out-of-range values) for testing error handling.
- **FR-017**: System MUST provide a review workflow fixture (`fixtures/review_submission_dataset.json`) containing a dataset in "pending review" state with complete provenance metadata for testing review transitions.
- **FR-018**: System MUST provide an admin approval fixture (`fixtures/admin_approval_dataset.json`) containing a dataset in "reviewed" state for testing publication approval workflows.
- **FR-019**: System MUST provide a round-trip reference dataset (`fixtures/round_trip_reference.xlsx`) containing examples of all GHFDB field types and optional fields for testing export-import cycles.

#### Schema Mapping Test Requirements

- **FR-020**: System MUST provide tests that validate each accessor path documented in `docs/ghfdb_fields.md` correctly retrieves the corresponding GHFDB field value.
- **FR-021**: Schema mapping tests MUST use the minimal fixture dataset to ensure all documented mappings are exercised.
- **FR-022**: Schema mapping tests MUST fail with clear error messages indicating which GHFDB field, accessor path, and expected vs actual value when mappings are incorrect.
- **FR-023**: System MUST provide tests for derived fields (quality scores, calculated values) that validate calculation logic against known input/output pairs from published literature.

#### Round-Trip Integrity Test Requirements

- **FR-024**: System MUST provide round-trip tests that import a dataset, export to IHFC format, re-import the export, and compare original vs re-imported data.
- **FR-025**: Round-trip tests MUST define explicit equivalence rules for mandatory fields (exact match required) and acceptable lossiness for optional fields (whitespace normalization, field reordering).
- **FR-026**: Round-trip tests MUST use the round-trip reference dataset containing diverse field types and edge cases.
- **FR-027**: Round-trip tests MUST report differences as test failures with clear indication of which field, record, and expected vs actual value differ.

#### CI Integration Requirements

- **FR-028**: System MUST configure pytest in `pyproject.toml` with test discovery paths, markers, and coverage thresholds.
- **FR-029**: System MUST provide a pytest configuration that runs unit tests by default (no marker) and requires explicit marker flags for integration, contract, and slow tests.
- **FR-030**: System MUST fail CI builds when unit test coverage falls below 80% for modified files (enforced via pytest-cov).

#### Documentation Requirements

- **FR-031**: System MUST maintain a testing guide (`docs/guides/testing-standards.md`) documenting test layer definitions, fixture locations, naming conventions, and how to run different test suites.
- **FR-032**: System MUST document acceptable lossiness rules for round-trip tests including specific transformations that are considered semantically equivalent.
- **FR-033**: System MUST document how to write contract tests including API request patterns, expected response schemas, and how to handle versioning.

### Key Entities

- **Test Layer**: Unit, Integration, or Contract - defines the scope and isolation level of a test.
- **Fixture Dataset**: A minimal, reusable test data file (Excel, JSON, or Django fixture) representing a specific workflow state (clean import, invalid data, pending review, approved).
- **Test Marker**: Pytest marker (e.g., `@pytest.mark.integration`) used to categorize and selectively run tests.
- **Accessor Path**: Django ORM query path (e.g., `HeatFlowSite.location.point`) documented in `docs/ghfdb_fields.md` that retrieves a GHFDB field value from the relational database.
- **Equivalence Rule**: A documented rule defining whether two data values are considered equivalent for round-trip testing (e.g., "whitespace normalization is acceptable, numeric precision must match within 0.0001").

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new feature specification referencing "unit tests in `tests/test_<app>/`" or "integration tests with minimal fixture" has unambiguous meaning - developers can locate the correct directory and fixture file without asking for clarification.
- **SC-002**: Running `pytest` (no arguments) executes only fast unit tests and completes in under 30 seconds for the entire test suite, providing rapid feedback during development.
- **SC-003**: Running `pytest -m integration` executes the complete import → review → approval → export workflow using minimal fixtures and completes in under 2 minutes, validating the core data lifecycle works end-to-end.
- **SC-004**: 100% of accessor paths documented in `docs/ghfdb_fields.md` have corresponding schema mapping tests that validate the path correctly retrieves the GHFDB field value.
- **SC-005**: Round-trip integrity tests import, export, and re-import the reference dataset and pass with zero mandatory field differences, documenting any acceptable lossiness (whitespace, field order) explicitly in test assertions.
- **SC-006**: Contract tests validate that all public API endpoints return responses matching the documented OpenAPI schema, catching breaking changes before they reach production.
- **SC-007**: CI builds fail when unit test coverage for modified files falls below 80%, preventing untested code from merging.
- **SC-008**: Test failures provide actionable error messages including which test failed, what was expected, what was received, and how to reproduce (file path, command, input data).

## Assumptions *(optional)*

- The existing pytest configuration in `pyproject.toml` will be extended, not replaced entirely.
- Fixture datasets will be maintained as static files (Excel, JSON) in the repository, not generated dynamically during tests.
- Schema mapping tests assume `docs/ghfdb_fields.md` is the authoritative source of truth for accessor paths.
- Round-trip tests assume the IHFC export format is stable and documented separately in the P2-04 export contract spec.
- Contract tests assume an OpenAPI/JSON schema definition exists or will be created as part of the P4-01 public API contract spec.
- Test execution time targets (30 seconds for unit tests, 2 minutes for integration tests) assume tests run on a standard developer laptop (not optimized CI hardware).
- Database-dependent unit tests will use Django's test database with transaction rollback, not a separate test database instance.

## Out of Scope *(optional)*

- **Performance/load testing**: Validating system behavior under high concurrent load is not part of this testing infrastructure spec.
- **End-to-end UI testing**: Browser-based testing with Selenium/Playwright is not included; this spec focuses on API and backend testing.
- **Mutation testing**: Using tools like mutmut to validate test effectiveness by introducing code mutations is valuable but not required for initial infrastructure.
- **Property-based testing**: Using Hypothesis for generative property-based testing is encouraged but not mandated in initial conventions.
- **Visual regression testing**: Comparing screenshots of UI components is not part of this backend-focused testing spec.
- **Security testing**: Penetration testing, vulnerability scanning, and security-specific test suites are important but outside the scope of baseline infrastructure conventions.
- **Test data generation tooling**: Automatic generation of fixture datasets from schemas (e.g., using factory_boy patterns) may be added later but is not required for initial fixtures.

## Dependencies *(optional)*

- **P0-01 Documentation Infrastructure**: Testing conventions reference `docs/guides/testing-standards.md` and assume the documentation structure is established.
- **Constitution Principle VII**: This spec implements the Test-Driven Development mandate requiring pytest-based TDD practices.
- **docs/ghfdb_fields.md**: Schema mapping tests depend on this file being accurate and complete.
- **pyproject.toml pytest configuration**: This spec extends the existing pytest configuration with markers and coverage thresholds.
- **Existing test structure**: This spec formalizes and extends the current ad-hoc test organization under `tests/test_*` directories.

## References *(optional)*

- **pytest documentation**: <https://docs.pytest.org/> - Official pytest testing framework documentation
- **pytest markers**: <https://docs.pytest.org/en/stable/how-to/mark.html> - Using markers to categorize tests
- **pytest fixtures**: <https://docs.pytest.org/en/stable/how-to/fixtures.html> - Fixture documentation
- **pytest-django**: <https://pytest-django.readthedocs.io/> - Django-specific pytest plugin
- **pytest-cov**: <https://pytest-cov.readthedocs.io/> - Coverage plugin for pytest
- **Django testing documentation**: <https://docs.djangoproject.com/en/5.0/topics/testing/> - Django testing patterns
- **Constitution Principle VII**: `.specify/memory/constitution.md` - Test-Driven Development mandate
- **Fuchs et al. (2023)**: Section 3.4 - Quality scoring evaluation scheme referenced in schema mapping tests
