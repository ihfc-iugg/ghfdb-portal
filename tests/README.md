# Tests Directory Structure

This directory contains all tests for the Global Heat Flow Database project, organized into three layers: unit tests, integration tests, and contract tests.

## Test Layers

### Unit Tests (Fast, Isolated)

- **Purpose**: Test individual functions, methods, and classes in isolation
- **Location**: `tests/test_<app_name>/test_<module>.py` (e.g., `tests/test_heat_flow/test_models.py`)
- **Characteristics**: No database access (unless marked `@pytest.mark.django_db`), no external services, fast execution (<5 seconds per module)
- **Run with**: `pytest` (default - runs unit tests only)

### Integration Tests (Full Stack)

- **Purpose**: Test complete workflows and component interactions
- **Location**: `tests/test_<app_name>/test_<workflow>_integration.py` (e.g., `tests/test_ghfdb/test_import_workflow_integration.py`)
- **Characteristics**: Full Django stack, database, fixtures, test complete data lifecycle
- **Marker**: `@pytest.mark.integration`
- **Run with**: `pytest -m integration`

### Contract Tests (API Validation)

- **Purpose**: Validate API response schemas and backward compatibility
- **Location**: `tests/contracts/test_<api_area>_contract.py` (e.g., `tests/contracts/test_public_api_contract.py`)
- **Characteristics**: Validate response structure, field types, error formats
- **Marker**: `@pytest.mark.contract`
- **Run with**: `pytest -m contract`

## Directory Structure

```
tests/
├── __init__.py                 # Main tests package
├── conftest.py                 # Shared pytest fixtures
├── README.md                   # This file
│
├── test_heat_flow/            # Unit tests for heat_flow app
│   ├── __init__.py
│   ├── test_factories.py      # Factory tests
│   ├── test_models.py         # Model tests
│   ├── test_views.py          # View tests
│   └── test_validation.py     # Validation logic tests
│
├── test_ghfdb/                # Tests for ghfdb app
│   ├── __init__.py
│   ├── test_importer.py       # Import functionality tests
│   ├── test_models.py         # Model tests
│   ├── test_views.py          # View tests
│   ├── test_import_workflow_integration.py    # Integration tests
│   ├── test_schema_mapping.py                 # Schema mapping validation
│   ├── test_round_trip_integrity.py           # Export-import integrity
│   └── data/                  # Test data files
│       ├── importer_fail.xlsx
│       ├── importer_fail_single_row.xlsx
│       ├── importer_success.xlsx
│       ├── minimal_ghfdb_import.xlsx
│       ├── invalid_ghfdb_import.xlsx
│       └── round_trip_reference.xlsx
│
├── test_review/               # Tests for review app
│   ├── __init__.py
│   ├── test_models.py         # Model tests
│   └── test_review_workflow_integration.py    # Review workflow integration tests
│
└── contracts/                 # Contract tests
    ├── __init__.py
    └── test_public_api_contract.py    # Public API schema validation
```

## Running Tests

### Run unit tests (default - fast feedback)

```bash
pytest
# or explicitly
pytest -m "not integration and not contract and not slow"
```

### Run integration tests

```bash
pytest -m integration
```

### Run contract tests

```bash
pytest -m contract
```

### Run all tests

```bash
pytest -m ""
```

### Run specific test files

```bash
# Unit tests only
pytest tests/test_heat_flow/test_models.py -v

# Integration tests only
pytest tests/test_ghfdb/test_import_workflow_integration.py -v
```

### Run with coverage

```bash
# Unit tests with coverage
pytest --cov=project --cov-report=term --cov-report=html

# All tests with coverage
pytest -m "" --cov=project --cov-report=term --cov-report=html
```

### Run tests marked as slow

```bash
pytest -m slow
```

## Test Markers

Tests can be marked with decorators to categorize them:

- **`@pytest.mark.integration`**: Integration tests requiring full Django stack and database
- **`@pytest.mark.contract`**: Contract tests validating API response schemas
- **`@pytest.mark.slow`**: Tests taking >5 seconds (excluded from default run)
- **`@pytest.mark.external`**: Tests requiring external services (skip when unavailable)
- **`@pytest.mark.django_db`**: Tests requiring database access (use on unit tests only when necessary)

Example:

```python
@pytest.mark.integration
@pytest.mark.django_db
def test_import_workflow_happy_path():
    # Test implementation
    pass
```

## Test Naming Conventions

### File Names

- Unit tests: `test_<module>.py` (e.g., `test_models.py`, `test_views.py`)
- Integration tests: `test_<workflow>_integration.py` (e.g., `test_import_workflow_integration.py`)
- Contract tests: `test_<api_area>_contract.py` (e.g., `test_public_api_contract.py`)

### Test Function Names

Follow the pattern: `test_<action>_<condition>_<expected_result>`

Examples:

- `test_import_invalid_template_raises_validation_error`
- `test_validate_coordinates_negative_latitude_fails`
- `test_calculate_u_score_with_known_values_returns_expected_score`

### Test Class Names

When grouping related tests: `class Test<FeatureName>`

Example:

```python
class TestQualityScoreCalculation:
    def test_u_score_calculation_reference_case(self):
        pass

    def test_m_score_calculation_reference_case(self):
        pass
```

### Fixture Names

Use lowercase with underscores describing what they provide:

```python
@pytest.fixture
def minimal_dataset():
    return Dataset.objects.create(name="Minimal Test Dataset")

@pytest.fixture
def invalid_coordinates():
    return {"latitude": 95, "longitude": 200}  # Invalid values
```

## Test Data Files

Test data files are organized within each app's test directory under a `data/` subdirectory. This keeps test data close to the tests that use it while maintaining organization.

### Available Fixtures

See `fixtures/README.md` for descriptions of shared fixture datasets:

- `fixtures/minimal_ghfdb_import.xlsx`: 5 heat flow sites with complete mandatory fields (happy path)
- `fixtures/invalid_ghfdb_import.xlsx`: 5 validation error cases
- `fixtures/review_submission_dataset.json`: Dataset in "pending review" state
- `fixtures/admin_approval_dataset.json`: Dataset in "reviewed" state
- `fixtures/round_trip_reference.xlsx`: 10 sites covering all GHFDB field types

## Adding New Tests

When adding new tests:

1. **Choose the right layer**: Unit (fast, isolated), Integration (workflow), or Contract (API)
2. **Place in appropriate directory**: `tests/test_<app>/` or `tests/contracts/`
3. **Follow naming conventions**: `test_*.py`, `test_<action>_<condition>_<expected_result>`
4. **Add appropriate markers**: `@pytest.mark.integration`, `@pytest.mark.contract`, etc.
5. **Use descriptive names**: Test names should clearly describe what is being tested
6. **Include docstrings**: Explain test purpose and acceptance criteria
7. **Use fixtures**: Load test data from conftest.py or local fixtures
8. **Follow TDD**: Write tests FIRST (ensure they fail), then implement

## Documentation

For detailed testing conventions, patterns, and examples, see:

- `docs/guides/testing-standards.md`: Complete testing guide with patterns and examples
- `fixtures/README.md`: Fixture dataset documentation and update process
- `.specify/memory/constitution.md`: Constitution Principle VII (Test-Driven Development)
