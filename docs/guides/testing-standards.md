# Testing Standards & Conventions

**Version**: 1.0
**Last Updated**: 2026-01-05
**Applies To**: Global Heat Flow Database (GHFDB) Project

## Table of Contents

1. [Test Pyramid & Strategy](#test-pyramid--strategy)
2. [TDD Workflow](#tdd-workflow)
3. [Test Layer Definitions](#test-layer-definitions)
4. [Unit Test Conventions](#unit-test-conventions)
5. [Integration Test Conventions](#integration-test-conventions)
6. [Contract Test Conventions](#contract-test-conventions)
7. [Parametrized Testing Patterns](#parametrized-testing-patterns)
8. [Fixture Conventions](#fixture-conventions)
9. [Database Testing Policy](#database-testing-policy)
10. [Code Coverage Guidelines](#code-coverage-guidelines)

---

## Test Pyramid & Strategy

The GHFDB testing strategy follows the **Test Pyramid** model, prioritizing fast unit tests at the base and fewer integration/contract tests at higher levels.

```
         /\
        /  \  Contract Tests (API schema validation)
       /____\
      /      \  Integration Tests (full-stack workflows)
     /________\
    /          \  Unit Tests (isolated functions/classes)
   /____________\
```

### Layer Distribution

- **Unit Tests (70-80%)**: Fast, isolated, no external dependencies
- **Integration Tests (15-25%)**: Full Django stack, database transactions
- **Contract Tests (5-10%)**: Public API endpoint validation

### Benefits

- **Fast feedback**: Unit tests run in <5 seconds, enabling rapid TDD cycles
- **Reliable CI**: Fewer integration tests means more stable builds
- **Clear failures**: Test failures pinpoint exact component issues
- **Cost efficiency**: Unit tests are cheap to maintain and debug

---

## TDD Workflow

Test-Driven Development (TDD) is the **required** development approach for all new features (Constitution Principle VII).

### Red-Green-Refactor Cycle

```
1. RED:   Write a failing test that defines desired behavior
2. GREEN: Write minimal code to make the test pass
3. REFACTOR: Improve code quality while keeping tests green
```

### Practical Example

```python
# Step 1 (RED): Write failing test
def test_normalize_latitude_handles_northern_hemisphere():
    """Latitude normalization should return positive values for N hemisphere."""
    result = normalize_latitude("45.5N")
    assert result == 45.5  # FAILS - function doesn't exist yet

# Step 2 (GREEN): Minimal implementation
def normalize_latitude(lat_str):
    value = float(lat_str[:-1])
    return value if lat_str.endswith('N') else -value

# Step 3 (REFACTOR): Add validation, edge cases, documentation
def normalize_latitude(lat_str):
    """
    Convert latitude string with hemisphere suffix to decimal degrees.

    Args:
        lat_str: Latitude with N/S suffix (e.g., "45.5N", "12.3S")

    Returns:
        float: Decimal degrees (positive=North, negative=South)

    Raises:
        ValueError: If format invalid or value out of range [-90, 90]
    """
    if not isinstance(lat_str, str) or len(lat_str) < 2:
        raise ValueError(f"Invalid latitude format: {lat_str}")

    hemisphere = lat_str[-1].upper()
    if hemisphere not in ('N', 'S'):
        raise ValueError(f"Latitude must end with N or S: {lat_str}")

    try:
        value = float(lat_str[:-1])
    except ValueError:
        raise ValueError(f"Invalid numeric value in latitude: {lat_str}")

    if not -90 <= value <= 90:
        raise ValueError(f"Latitude out of range [-90, 90]: {value}")

    return value if hemisphere == 'N' else -value
```

### TDD Best Practices

1. **Write the test first**: Never write production code without a failing test
2. **One assertion per test**: Tests should verify a single behavior
3. **Test behavior, not implementation**: Tests should survive refactoring
4. **Name tests descriptively**: `test_action_condition_expectedResult`
5. **Keep tests simple**: Test code should be easier to read than production code

---

## Test Layer Definitions

### Unit Tests

**Purpose**: Test individual functions/methods in complete isolation

**Characteristics**:

- No database access (@pytest.mark.django_db NOT used)
- No network calls (external APIs mocked)
- No file I/O (use in-memory data structures)
- Execution time: <5 seconds for entire suite
- Run by default: `pytest` (no markers needed)

**Example**:

```python
from heat_flow.utils import calculate_U_score

def test_calculate_u_score_perfect_quality():
    """U-score should be U1 for perfect temperature measurement."""
    result = calculate_U_score(
        method="Logging",
        uncertainty=0.5,
        shutin_time=24
    )
    assert result == "U1"

def test_calculate_u_score_poor_quality():
    """U-score should be U5 for unreliable measurements."""
    result = calculate_U_score(
        method="Unknown",
        uncertainty=15.0,
        shutin_time=0
    )
    assert result == "U5"
```

### Integration Tests

**Purpose**: Test complete workflows through Django ORM, views, and forms

**Characteristics**:

- Uses Django test database (automatic transaction rollback)
- Tests multiple components working together
- Marked with `@pytest.mark.integration`
- Execution time: <2 minutes for suite
- Run explicitly: `pytest -m integration`

**Example**:

```python
import pytest
from django.core.management import call_command
from fairdm.core.models import Dataset
from ghfdb.resources import GHFDBResource
from ghfdb.views import GHFDBImportFormat

@pytest.mark.integration
def test_import_minimal_dataset_creates_heat_flow_sites(
    minimal_ghfdb_import_data,
    django_db_blocker
):
    """Integration test: GHFDB import should create HeatFlowSite instances."""
    with django_db_blocker.unblock():
        # Arrange
        dataset = Dataset.objects.create(name="Integration Test Dataset")
        resource = GHFDBResource(dataset)
        input_format = GHFDBImportFormat(encoding="utf-8-sig")
        input_data = input_format.create_dataset(minimal_ghfdb_import_data)

        # Act
        result = resource.import_data(input_data, raise_errors=True)

        # Assert
        assert not result.has_errors()
        assert HeatFlowSite.objects.filter(dataset=dataset).count() == 5
```

### Contract Tests

**Purpose**: Validate public API responses match documented schemas

**Characteristics**:

- Tests API endpoint response structure
- Verifies backward compatibility
- Marked with `@pytest.mark.contract`
- No business logic testing (only schema validation)
- Run explicitly: `pytest -m contract`

**Example**:

```python
import pytest
from django.urls import reverse

@pytest.mark.contract
@pytest.mark.django_db
def test_dataset_api_response_schema(client, admin_approval_dataset):
    """Dataset API must return required fields with correct types."""
    url = reverse('api:dataset-detail', kwargs={'pk': admin_approval_dataset.pk})
    response = client.get(url)

    assert response.status_code == 200
    data = response.json()

    # Validate schema contract
    assert 'uuid' in data
    assert 'name' in data
    assert 'visibility' in data
    assert isinstance(data['uuid'], str)
    assert isinstance(data['name'], str)
    assert isinstance(data['visibility'], int)
```

---

## Unit Test Conventions

### File Organization

```
tests/
├── test_ghfdb/
│   ├── test_resources.py          # GHFDBResource unit tests
│   ├── test_validation.py         # Validation function unit tests
│   └── test_import_format.py      # Import format parser tests
├── test_heat_flow/
│   ├── test_models.py              # Model method unit tests (no DB)
│   ├── test_quality_scores.py     # Quality score calculation
│   ├── test_coordinates.py        # Coordinate normalization
│   └── test_vocabularies.py       # Controlled vocabulary helpers
└── test_review/
    ├── test_permissions.py         # Permission checking logic
    └── test_state_machine.py       # Review state transitions (no DB)
```

### Naming Patterns

**Test Functions**: `test_<action>_<condition>_<expected_result>`

```python
# Good: Descriptive, self-documenting
def test_normalize_latitude_with_north_suffix_returns_positive():
    pass

def test_normalize_latitude_with_south_suffix_returns_negative():
    pass

def test_normalize_latitude_with_invalid_range_raises_value_error():
    pass

# Bad: Vague, requires reading test body
def test_normalize():
    pass

def test_latitude():
    pass

def test_error():
    pass
```

**Test Classes**: `Test<ComponentName>`

```python
class TestCoordinateNormalization:
    """Unit tests for coordinate normalization functions."""

    def test_latitude_north_hemisphere(self):
        pass

    def test_latitude_south_hemisphere(self):
        pass

    def test_longitude_east_hemisphere(self):
        pass
```

### Test Isolation Principles

1. **No shared state**: Each test must be independent
2. **No test order dependency**: Tests can run in any order
3. **Clean setup/teardown**: Use fixtures for repeatable setup
4. **Mock external dependencies**: Never call real APIs or databases

```python
# Good: Isolated test with mocked dependencies
from unittest.mock import Mock, patch

def test_fetch_literature_handles_network_error():
    """Literature fetcher should log error and return None on network failure."""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.ConnectionError("Network unreachable")

        result = fetch_literature_by_doi("10.1234/example")

        assert result is None
        assert mock_get.called

# Bad: Test depends on external API (slow, flaky)
def test_fetch_literature_real_api():
    """DON'T DO THIS - relies on external service."""
    result = fetch_literature_by_doi("10.1234/example")  # Calls real API!
    assert result is not None
```

### Mocking Strategies

**Use `unittest.mock` for external dependencies:**

```python
from unittest.mock import Mock, patch, MagicMock

# Mock function return value
@patch('module.function_name')
def test_with_mocked_function(mock_function):
    mock_function.return_value = "mocked result"
    assert call_code_using_function() == "expected"

# Mock class instance
@patch('module.ClassName')
def test_with_mocked_class(MockClass):
    mock_instance = MockClass.return_value
    mock_instance.method.return_value = 42
    assert code_using_class() == 42

# Mock Django ORM queries (when not using @pytest.mark.django_db)
@patch('heat_flow.models.HeatFlowSite.objects')
def test_query_logic_without_database(mock_objects):
    mock_objects.filter.return_value.count.return_value = 5
    assert get_site_count() == 5
```

---

## Integration Test Conventions

### Workflow Testing Patterns

Integration tests validate complete user workflows through the Django stack.

```python
import pytest
from django.contrib.auth import get_user_model
from fairdm.core.models import Dataset

@pytest.mark.integration
@pytest.mark.django_db
def test_review_submission_workflow():
    """Test complete dataset submission to review workflow."""
    # Arrange: Create user and dataset
    User = get_user_model()
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com'
    )
    dataset = Dataset.objects.create(
        name="Test Dataset",
        visibility=0  # Private
    )

    # Act: Submit for review
    review = Review.objects.create(
        dataset=dataset,
        status=Review.STATUS_CHOICES.PENDING
    )
    review.reviewers.add(user)

    # Assert: State transitions correctly
    assert dataset.visibility == 0  # Still private
    assert review.status == Review.STATUS_CHOICES.PENDING
    assert user in review.reviewers.all()
```

### Fixture Usage in Integration Tests

Use the predefined fixtures from `tests/conftest.py`:

```python
@pytest.mark.integration
def test_import_workflow_with_minimal_fixture(
    minimal_ghfdb_import_data,  # Excel file fixture
    ghfdb_dataset               # Empty dataset fixture
):
    """Import minimal fixture and validate created objects."""
    resource = GHFDBResource(ghfdb_dataset)
    input_format = GHFDBImportFormat(encoding="utf-8-sig")
    input_data = input_format.create_dataset(minimal_ghfdb_import_data)

    result = resource.import_data(input_data)

    assert not result.has_errors()
    assert HeatFlowSite.objects.count() == 5
```

### Assertion Strategies

**State Transitions**: Verify workflow state changes

```python
# Before action
assert dataset.visibility == 0  # Private

# Perform action
approve_dataset(dataset)

# After action
assert dataset.visibility == 1  # Public
assert dataset.review.status == Review.STATUS_CHOICES.COMPLETE
```

**Data Preservation**: Ensure data survives round-trip

```python
# Original data
original_sites = list(HeatFlowSite.objects.values('name', 'lat', 'lon'))

# Export and re-import
export_data = resource.export()
reimport_resource = GHFDBResource(new_dataset)
reimport_resource.import_data(export_data)

# Verify preservation
reimported_sites = list(HeatFlowSite.objects.filter(dataset=new_dataset).values('name', 'lat', 'lon'))
assert original_sites == reimported_sites
```

**Relationship Integrity**: Check foreign key relationships

```python
site = HeatFlowSite.objects.first()
assert site.dataset == ghfdb_dataset
assert site.measurements.count() > 0
assert site.measurements.first().sample == site
```

### Test Execution Flow

Integration tests follow a consistent **Arrange-Act-Assert** pattern:

```python
@pytest.mark.integration
@pytest.mark.django_db
def test_full_workflow_import_to_export():
    """End-to-end test: import → review → approve → export."""
    # Arrange: Set up initial state
    User = get_user_model()
    admin_user = User.objects.create_user(
        username='admin',
        is_staff=True
    )
    dataset = Dataset.objects.create(name="E2E Test Dataset")

    # Act 1: Import data
    resource = GHFDBResource(dataset)
    input_format = GHFDBImportFormat(encoding="utf-8-sig")
    input_data = input_format.create_dataset(minimal_ghfdb_import_data)
    import_result = resource.import_data(input_data)

    # Assert 1: Import successful
    assert not import_result.has_errors()
    assert HeatFlowSite.objects.filter(dataset=dataset).count() == 5

    # Act 2: Submit for review
    review = Review.objects.create(
        dataset=dataset,
        status=Review.STATUS_CHOICES.PENDING
    )

    # Assert 2: Review created
    assert review.status == Review.STATUS_CHOICES.PENDING

    # Act 3: Admin approval
    review.status = Review.STATUS_CHOICES.COMPLETE
    review.approved_by = admin_user
    review.save()
    dataset.visibility = 1  # Public
    dataset.save()

    # Assert 3: Approved and published
    assert dataset.visibility == 1
    assert review.status == Review.STATUS_CHOICES.COMPLETE

    # Act 4: Export data
    export_data = resource.export()

    # Assert 4: Export contains all sites
    assert len(export_data.dict) == 5  # 5 sites exported
```

### Timing Requirements

Integration tests must complete within **2 minutes** per suite:

- Single integration test: <10 seconds
- Full integration suite: <120 seconds
- Use `@pytest.mark.slow` for tests >30 seconds

**Performance Tips**:

```python
# ✅ Good: Reuse database fixtures
@pytest.fixture(scope='module')
def shared_dataset(django_db_blocker):
    with django_db_blocker.unblock():
        return Dataset.objects.create(name="Shared Dataset")

# ❌ Avoid: Creating database objects in every test
def test_workflow_step_1():
    dataset = Dataset.objects.create(...)  # Slow!
```

### Using Predefined Fixtures

The `tests/fixtures/` directory contains ready-to-use test data:

**Excel Fixtures** (see `tests/fixtures/README.md` for details):

```python
@pytest.mark.integration
def test_import_minimal_fixture(minimal_ghfdb_import_data):
    """minimal_ghfdb_import.xlsx: 5 sites, happy path validation."""
    # Use for testing successful imports
    pass

def test_import_invalid_fixture(invalid_ghfdb_import_data):
    """invalid_ghfdb_import.xlsx: 5 error cases."""
    # Use for testing error detection
    pass

def test_round_trip_fixture(round_trip_reference_data):
    """round_trip_reference.xlsx: 10 comprehensive sites."""
    # Use for export/re-import validation
    pass
```

**JSON Fixtures** (Django models):

```python
@pytest.mark.integration
@pytest.mark.django_db
def test_review_workflow(review_submission_dataset):
    """review_submission_dataset.json: Dataset with pending review."""
    dataset = Dataset.objects.get(pk=100)
    assert dataset.visibility == 0  # Private
    assert dataset.review.status == Review.STATUS_CHOICES.PENDING

def test_admin_approval(admin_approval_dataset):
    """admin_approval_dataset.json: Dataset approved for publication."""
    dataset = Dataset.objects.get(pk=200)
    assert dataset.visibility == 1  # Public
    assert dataset.review.status == Review.STATUS_CHOICES.COMPLETE
```

### Workflow Gates and Authorization

Test permission checks in multi-step workflows:

```python
@pytest.mark.integration
@pytest.mark.django_db
def test_export_without_approval_fails():
    """Export should fail for unapproved datasets."""
    # Arrange: Private dataset
    dataset = Dataset.objects.create(
        name="Private Dataset",
        visibility=0  # Private
    )

    # Act: Attempt export
    resource = GHFDBResource(dataset)
    export_data = resource.export()

    # Assert: Export blocked or returns empty
    assert len(export_data.dict) == 0  # No data exported

@pytest.mark.integration
@pytest.mark.django_db
def test_approve_for_publication_requires_admin():
    """Only admin users can approve datasets."""
    # Arrange: Regular user and dataset
    User = get_user_model()
    regular_user = User.objects.create_user(
        username='regularuser',
        is_staff=False
    )
    dataset = Dataset.objects.create(name="Test Dataset")
    review = Review.objects.create(
        dataset=dataset,
        status=Review.STATUS_CHOICES.PENDING
    )

    # Act & Assert: Regular user cannot approve
    with pytest.raises(PermissionError):
        review.approve(user=regular_user)

    # Act & Assert: Admin user can approve
    admin_user = User.objects.create_user(
        username='admin',
        is_staff=True
    )
    review.approve(user=admin_user)  # Should succeed
    assert review.status == Review.STATUS_CHOICES.COMPLETE
```

---

## Contract Test Conventions

### API Schema Validation Patterns

Contract tests protect external API consumers from breaking changes by validating:

- **Field presence**: Required fields must always be present
- **Field types**: Field types must remain consistent across versions
- **Response structure**: Objects, arrays, pagination must follow documented format
- **Nullable fields**: Explicit `null` values instead of field omission

**Example: Dataset Detail Response**

```python
import pytest

@pytest.mark.contract
@pytest.mark.django_db
def test_get_dataset_response_schema(client, admin_approval_dataset):
    """GET /api/v1/datasets/{id}/ must return consistent schema."""
    response = client.get(f'/api/v1/datasets/{admin_approval_dataset.pk}/')

    assert response.status_code == 200
    data = response.json()

    # Required fields (must be present)
    assert 'uuid' in data
    assert 'name' in data
    assert 'visibility' in data
    assert 'created_date' in data

    # Field type validation
    assert isinstance(data['uuid'], str)
    assert isinstance(data['name'], str)
    assert isinstance(data['visibility'], int)
    assert isinstance(data['created_date'], str)  # ISO 8601

    # Nullable field handling (explicit null, not omitted)
    assert 'description' in data  # Must be present even if null
    if data['description'] is not None:
        assert isinstance(data['description'], str)
```

**Example: List Response Schema**

```python
@pytest.mark.contract
@pytest.mark.django_db
def test_dataset_list_response_schema(client):
    """GET /api/v1/datasets/ must return standard list response."""
    response = client.get('/api/v1/datasets/')

    assert response.status_code == 200
    data = response.json()

    # Pagination contract
    assert 'count' in data
    assert 'next' in data
    assert 'previous' in data
    assert 'results' in data

    # Type validation
    assert isinstance(data['count'], int)
    assert data['next'] is None or isinstance(data['next'], str)  # URL or null
    assert data['previous'] is None or isinstance(data['previous'], str)
    assert isinstance(data['results'], list)

    # Results structure (if not empty)
    if data['results']:
        first_item = data['results'][0]
        assert 'uuid' in first_item
        assert 'name' in first_item
```

### Standard Error Payload Format

All API errors must follow consistent schema to support client error handling.

**Error Contract Requirements**:

- **detail**: Human-readable error message (string, required)
- **error_code**: Machine-readable error code (string, optional but recommended)
- **timestamp**: ISO 8601 timestamp (string, optional)
- **field_errors**: Field-level validation errors (object, for 400 responses)

```python
@pytest.mark.contract
def test_unauthorized_request_error_contract(client):
    """HTTP 401 errors must include standard error payload."""
    response = client.get('/api/v1/datasets/999/')

    assert response.status_code == 401
    error = response.json()

    # Required error fields
    assert 'detail' in error
    assert isinstance(error['detail'], str)
    assert len(error['detail']) > 0  # Non-empty error message

    # Optional but recommended fields
    if 'error_code' in error:
        assert isinstance(error['error_code'], str)
        assert error['error_code'] in ['unauthorized', 'authentication_failed']

    if 'timestamp' in error:
        assert isinstance(error['timestamp'], str)
        # Validate ISO 8601 format
        from datetime import datetime
        datetime.fromisoformat(error['timestamp'].replace('Z', '+00:00'))

@pytest.mark.contract
def test_validation_error_payload_format(client):
    """HTTP 400 validation errors must include field-level details."""
    response = client.post('/api/v1/datasets/', json={'name': ''})  # Invalid: empty name

    assert response.status_code == 400
    error = response.json()

    # Field-level error contract
    assert 'detail' in error or 'field_errors' in error

    if 'field_errors' in error:
        assert isinstance(error['field_errors'], dict)
        # Each field error should be a list of error messages
        for field, messages in error['field_errors'].items():
            assert isinstance(messages, list)
            assert all(isinstance(msg, str) for msg in messages)
```

### API Versioning Guidance

**Versioning Strategy**: Maintain backward compatibility within major versions

**Additive Changes (Safe)**:

- Add new optional fields to responses
- Add new endpoints
- Add new optional query parameters
- Add new enum values (with fallback)

**Breaking Changes (Require Version Bump)**:

- Remove fields from responses
- Rename fields
- Change field types
- Make optional fields required
- Remove enum values
- Change response status codes
- Change error payload structure

**Testing Version Compatibility**:

```python
@pytest.mark.contract
def test_dataset_response_backward_compatible(client, admin_approval_dataset):
    """New fields must be optional, existing fields must remain."""
    response = client.get(f'/api/v1/datasets/{admin_approval_dataset.pk}/')
    data = response.json()

    # v1.0 contract fields (cannot be removed or changed)
    assert 'uuid' in data
    assert 'name' in data
    assert 'visibility' in data
    assert isinstance(data['uuid'], str)
    assert isinstance(data['name'], str)
    assert isinstance(data['visibility'], int)

    # v1.1 additions (optional fields)
    if 'created_date' in data:
        assert isinstance(data['created_date'], str)  # ISO 8601 format

    if 'updated_date' in data:
        assert isinstance(data['updated_date'], str)

@pytest.mark.contract
def test_deprecated_field_still_present(client):
    """Deprecated fields must remain until next major version."""
    response = client.get('/api/v1/datasets/')
    data = response.json()

    # Field deprecated in v1.3, marked for removal in v2.0
    # Must still be present in v1.x responses
    if data['results']:
        first_item = data['results'][0]
        assert 'old_field_name' in first_item, (
            "Deprecated field must remain until v2.0"
        )
```

**Deprecation Headers**:

```python
@pytest.mark.contract
def test_deprecated_endpoint_warning_header(client):
    """Deprecated endpoints must include Deprecation header."""
    response = client.get('/api/v1/old-endpoint/')

    # RFC 8594 Deprecation header
    assert 'Deprecation' in response.headers or 'Sunset' in response.headers

    if 'Deprecation' in response.headers:
        # Example: "Deprecation: true" or "Deprecation: @1672531200"
        assert response.headers['Deprecation']

    if 'Sunset' in response.headers:
        # RFC 8594: HTTP date indicating removal date
        # Example: "Sunset: Sat, 31 Dec 2024 23:59:59 GMT"
        assert response.headers['Sunset']
```

---

## Schema Mapping Test Conventions

Schema mapping tests validate that accessor paths documented in `docs/ghfdb_fields.md` correctly retrieve values from Django models and serialize to the GHFDB export format.

### Accessor Path Validation Patterns

Test that documented model accessors work correctly:

```python
import pytest
from ghfdb.models import HeatFlowSite
from fairdm.core.models import Dataset

@pytest.mark.django_db
def test_ghfdb_field_site_name_accessor_path():
    """
    Validate 'site_name' accessor path: HeatFlowSite.name

    This test ensures the documented accessor path in ghfdb_fields.md
    correctly retrieves the site name value.
    """
    # Arrange: Create test record
    dataset = Dataset.objects.create(name="Schema Test Dataset")
    site = HeatFlowSite.objects.create(
        dataset=dataset,
        name="Test Site Alpha",
        lat=45.0,
        lon=-120.0
    )

    # Act: Access field via documented path
    site_name = site.name  # Accessor path from ghfdb_fields.md

    # Assert: Value matches
    assert site_name == "Test Site Alpha"

@pytest.mark.django_db
def test_ghfdb_field_coordinates_accessor_path():
    """
    Validate 'latitude'/'longitude' accessor paths: HeatFlowSite.location.point

    Validates:
    - Accessor path works correctly
    - Coordinate precision (0.0001 degrees)
    - Point geometry correctly stores lat/lon
    """
    # Arrange: Create test record
    dataset = Dataset.objects.create(name="Coordinate Test Dataset")
    site = HeatFlowSite.objects.create(
        dataset=dataset,
        name="Coordinate Test Site",
        lat=45.123456,
        lon=-120.987654
    )

    # Act: Access coordinates via documented path
    # Note: Actual accessor depends on model structure
    # This demonstrates the testing pattern
    latitude = site.lat
    longitude = site.lon

    # Assert: Values match within precision tolerance
    assert abs(latitude - 45.123456) < 0.0001, (
        f"Latitude precision error: expected 45.123456, got {latitude}"
    )
    assert abs(longitude - (-120.987654)) < 0.0001, (
        f"Longitude precision error: expected -120.987654, got {longitude}"
    )

@pytest.mark.django_db
def test_ghfdb_field_heat_flow_value_accessor_path():
    """
    Validate 'heat_flow' accessor path: SurfaceHeatFlow.value

    Validates:
    - Accessor path works correctly
    - Value is numeric (float)
    - Units are preserved (mW/m²)
    """
    # Arrange: Create related models
    dataset = Dataset.objects.create(name="Heat Flow Test Dataset")
    site = HeatFlowSite.objects.create(
        dataset=dataset,
        name="Heat Flow Test Site",
        lat=45.0,
        lon=-120.0
    )

    # Create heat flow measurement
    # Note: Model structure may vary - this demonstrates the pattern
    from ghfdb.models import SurfaceHeatFlow
    heat_flow = SurfaceHeatFlow.objects.create(
        site=site,
        value=65.5,  # mW/m²
        uncertainty=2.0
    )

    # Act: Access value via documented path
    hf_value = heat_flow.value

    # Assert: Value matches
    assert isinstance(hf_value, (int, float)), "Heat flow must be numeric"
    assert abs(hf_value - 65.5) < 0.01, (
        f"Heat flow value error: expected 65.5, got {hf_value}"
    )
```

### Derived Field Testing (Quality Scores)

Quality scores are derived fields calculated from measurement metadata. Test these calculations with known reference values from literature (Fuchs et al. 2023).

**U-Score Reference Test**:

```python
import pytest

@pytest.mark.django_db
def test_u_score_calculation_reference_case():
    """
    Validate U-score calculation with known reference values.

    Reference: Fuchs et al. (2023) "Quality evaluation scheme for GHFDB"
    Section 3.2, Table 2: U-score categorization criteria

    Known Test Case:
    - Method: Logging
    - Uncertainty: 1.5 mW/m²
    - Shutin time: 48 hours
    - Expected U-score: U1 (highest quality)
    """
    from ghfdb.models import HeatFlowSite, HeatFlowMeasurement

    # Arrange: Create site with U1-quality measurement
    dataset = Dataset.objects.create(name="U-Score Reference Test")
    site = HeatFlowSite.objects.create(
        dataset=dataset,
        name="U1 Reference Site",
        lat=45.0,
        lon=-120.0
    )

    measurement = HeatFlowMeasurement.objects.create(
        site=site,
        method="Logging",
        uncertainty_mw_m2=1.5,
        shutin_time_hours=48
    )

    # Act: Calculate U-score
    u_score = measurement.calculate_u_score()

    # Assert: Matches reference value
    assert u_score == "U1", (
        f"Expected U1 for Logging method, 1.5 mW/m² uncertainty, 48h shutin. "
        f"Got {u_score}. Check calculation against Fuchs et al. 2023 Table 2."
    )

@pytest.mark.django_db
def test_m_score_calculation_reference_case():
    """
    Validate M-score calculation with known reference values.

    Reference: Fuchs et al. (2023) "Quality evaluation scheme for GHFDB"
    Section 3.3, Table 3: M-score categorization criteria

    Known Test Case:
    - Method: Interval method
    - Number of measurements: 12
    - Documentation level: Full
    - Expected M-score: M1 (highest quality)
    """
    from ghfdb.models import HeatFlowSite, HeatFlowMeasurement

    # Arrange: Create site with M1-quality methodology
    dataset = Dataset.objects.create(name="M-Score Reference Test")
    site = HeatFlowSite.objects.create(
        dataset=dataset,
        name="M1 Reference Site",
        lat=45.0,
        lon=-120.0
    )

    measurement = HeatFlowMeasurement.objects.create(
        site=site,
        method="Interval method",
        num_measurements=12,
        documentation_level="Full"
    )

    # Act: Calculate M-score
    m_score = measurement.calculate_m_score()

    # Assert: Matches reference value
    assert m_score == "M1", (
        f"Expected M1 for Interval method, 12 measurements, Full documentation. "
        f"Got {m_score}. Check calculation against Fuchs et al. 2023 Table 3."
    )
```

### Schema Mapping Test Strategy

1. **Priority Fields**: Test critical fields first (site_name, coordinates, heat_flow, quality_scores)
2. **Incremental Coverage**: Add tests for remaining fields over time (target 10-15 initially)
3. **Reference Documentation**: Each test references the specific row in `docs/ghfdb_fields.md`
4. **Precision Tolerance**: Document acceptable precision for numeric fields (0.0001 for coordinates, 0.01 for heat flow)
5. **Failure Reporting**: Include accessor path in assertion messages for debugging

---

## Parametrized Testing Patterns

Parametrized tests reduce code duplication and increase test coverage.

### Basic Parametrization

```python
import pytest

@pytest.mark.parametrize("lat_str,expected", [
    ("45.5N", 45.5),
    ("12.3S", -12.3),
    ("0.0N", 0.0),
    ("90.0N", 90.0),
    ("90.0S", -90.0),
])
def test_normalize_latitude_multiple_cases(lat_str, expected):
    """Latitude normalization handles various valid inputs correctly."""
    result = normalize_latitude(lat_str)
    assert result == expected
```

### Parametrize with IDs (Better Test Names)

```python
@pytest.mark.parametrize("lat_str,expected", [
    ("45.5N", 45.5),
    ("12.3S", -12.3),
], ids=["northern_hemisphere", "southern_hemisphere"])
def test_normalize_latitude_by_hemisphere(lat_str, expected):
    """Test output shows: test_normalize_latitude_by_hemisphere[northern_hemisphere]"""
    result = normalize_latitude(lat_str)
    assert result == expected
```

### Multiple Parameters

```python
@pytest.mark.parametrize("method,uncertainty,shutin,expected_score", [
    ("Logging", 0.5, 24, "U1"),    # Perfect quality
    ("BHT", 2.0, 12, "U2"),         # Good quality
    ("BHT", 5.0, 6, "U3"),          # Moderate quality
    ("Unknown", 10.0, 0, "U5"),     # Poor quality
])
def test_u_score_calculation_quality_levels(method, uncertainty, shutin, expected_score):
    """U-score correctly categorizes measurement quality levels."""
    result = calculate_U_score(method, uncertainty, shutin)
    assert result == expected_score
```

### Error Case Parametrization

```python
@pytest.mark.parametrize("invalid_lat", [
    "95.0N",      # > 90
    "-100.0S",    # < -90
    "45.5",       # Missing hemisphere
    "ABC",        # Non-numeric
    "",           # Empty string
], ids=["too_large", "too_small", "missing_hemisphere", "non_numeric", "empty"])
def test_normalize_latitude_invalid_inputs_raise_value_error(invalid_lat):
    """Latitude normalization rejects invalid inputs."""
    with pytest.raises(ValueError):
        normalize_latitude(invalid_lat)
```

### Combining Multiple Parametrize Decorators

```python
@pytest.mark.parametrize("method", ["Logging", "BHT", "Thermistor"])
@pytest.mark.parametrize("uncertainty", [0.5, 1.0, 2.0])
def test_u_score_all_method_uncertainty_combinations(method, uncertainty):
    """Test U-score for all method/uncertainty combinations (3 × 3 = 9 tests)."""
    result = calculate_U_score(method, uncertainty, shutin_time=24)
    assert result in ["U1", "U2", "U3", "U4", "U5"]
```

---

## Fixture Conventions

### Fixture Naming

**Convention**: `lowercase_with_underscores`

```python
# Good fixture names
@pytest.fixture
def heat_flow_site():
    pass

@pytest.fixture
def authenticated_user():
    pass

@pytest.fixture
def minimal_ghfdb_import_data():
    pass

# Bad fixture names
@pytest.fixture
def HeatFlowSite():  # Looks like a class
    pass

@pytest.fixture
def User():  # Confusing with Django User model
    pass
```

### Fixture Scopes

Control fixture lifecycle with `scope` parameter:

```python
@pytest.fixture(scope="function")  # Default: created/destroyed per test
def temporary_file():
    file = open("temp.txt", "w")
    yield file
    file.close()
    os.remove("temp.txt")

@pytest.fixture(scope="class")  # Shared across test class methods
def database_connection():
    conn = connect_to_db()
    yield conn
    conn.close()

@pytest.fixture(scope="module")  # Created once per module
def expensive_computation():
    return compute_large_dataset()

@pytest.fixture(scope="session")  # Created once per test session
def django_db_setup(django_db_setup, django_db_blocker):
    """Load vocabularies once for entire session."""
    with django_db_blocker.unblock():
        Concept.preload()
```

### Fixture Dependencies

Fixtures can depend on other fixtures:

```python
@pytest.fixture
def dataset():
    return Dataset.objects.create(name="Test Dataset")

@pytest.fixture
def heat_flow_site(dataset):  # Depends on dataset fixture
    return HeatFlowSite.objects.create(
        name="Test Site",
        dataset=dataset
    )

@pytest.fixture
def heat_flow_measurement(heat_flow_site):  # Depends on heat_flow_site
    return SurfaceHeatFlow.objects.create(
        value=50.0,
        sample=heat_flow_site
    )
```

### Fixture Factories

Use fixture factories for creating multiple instances:

```python
@pytest.fixture
def make_heat_flow_site(ghfdb_dataset):
    """Factory fixture for creating multiple HeatFlowSite instances."""
    def _make_site(name=None, lat=None, lon=None):
        return HeatFlowSite.objects.create(
            name=name or "Test Site",
            location=Point(lon or 0.0, lat or 0.0),
            dataset=ghfdb_dataset
        )
    return _make_site

def test_multiple_sites(make_heat_flow_site):
    """Use factory to create multiple sites."""
    site1 = make_heat_flow_site(name="Site 1", lat=45.0, lon=-120.0)
    site2 = make_heat_flow_site(name="Site 2", lat=48.0, lon=-118.0)
    assert HeatFlowSite.objects.count() == 2
```

---

## Database Testing Policy

### When to Use @pytest.mark.django_db

**Unit tests (NO database)**:

- Testing pure functions (calculations, formatting)
- Testing business logic without persistence
- Testing validators that don't query DB
- Use mocks for ORM queries

**Integration tests (USE database)**:

- Testing Django ORM queries
- Testing model save() methods with database constraints
- Testing views/forms that interact with DB
- Testing complete workflows

### Examples

```python
# Unit test (NO @pytest.mark.django_db)
def test_calculate_heat_flow_from_gradient_and_conductivity():
    """Pure calculation - no database needed."""
    gradient = 30.0  # °C/km
    conductivity = 2.5  # W/(m·K)

    result = calculate_heat_flow(gradient, conductivity)

    assert result == 75.0  # mW/m²

# Integration test (USE @pytest.mark.django_db)
@pytest.mark.integration
@pytest.mark.django_db
def test_heat_flow_site_save_updates_quality_score():
    """Model save() method calculates quality score - needs DB."""
    site = HeatFlowSite.objects.create(
        name="Test Site",
        location=Point(-120.0, 45.0)
    )

    measurement = SurfaceHeatFlow.objects.create(
        value=50.0,
        uncertainty=5.0,
        sample=site
    )

    # Trigger save() to recalculate quality
    measurement.save()

    assert measurement.quality_score in ["U1", "U2", "U3", "U4", "U5"]
```

### Test Database Behavior

Django creates a **separate test database** with automatic transaction rollback:

1. **Before each test**: Transaction starts
2. **During test**: All database changes are made
3. **After test**: Transaction rolls back (database is clean)

```python
@pytest.mark.django_db
def test_database_rollback_behavior():
    """Database changes are rolled back after test."""
    # Create object
    site = HeatFlowSite.objects.create(name="Temp Site")
    assert HeatFlowSite.objects.count() == 1

    # After this test completes, rollback happens automatically
    # Next test will see count == 0
```

### Avoiding Database in Unit Tests

**Use mocks instead of database queries:**

```python
from unittest.mock import Mock, patch

# Bad: Unit test using database (slow, requires migrations)
@pytest.mark.django_db
def test_get_high_quality_sites_bad():
    """DON'T DO THIS in unit tests."""
    HeatFlowSite.objects.create(name="Site 1", quality="U1")
    sites = get_high_quality_sites()
    assert len(sites) == 1

# Good: Unit test with mocked ORM (fast, no database)
@patch('module.HeatFlowSite.objects')
def test_get_high_quality_sites_good(mock_objects):
    """Unit test with mocked queryset."""
    mock_qs = Mock()
    mock_qs.filter.return_value.values_list.return_value = ["Site 1"]
    mock_objects.filter.return_value = mock_qs

    sites = get_high_quality_sites()

    assert len(sites) == 1
    mock_objects.filter.assert_called_with(quality__in=["U1", "U2"])
```

---

## Code Coverage Guidelines

### Coverage Thresholds

- **Modified files**: 80% minimum (enforced by pytest-cov)
- **New files**: 90% recommended for new features
- **Legacy code**: No retroactive coverage requirement

### Running Coverage Reports

```bash
# Run tests with coverage
pytest --cov=project --cov-report=html

# View HTML report
open htmlcov/index.html

# Terminal coverage summary
pytest --cov=project --cov-report=term-missing
```

### Coverage Configuration

See `pyproject.toml` for coverage settings:

```toml
[tool.coverage.run]
source = ["project"]
omit = [
    "*/migrations/*",
    "*/tests/*",
    "*/admin.py",
]

[tool.coverage.report]
fail_under = 80
show_missing = true
skip_covered = false
```

### What to Cover

**DO test**:

- Business logic functions
- Model methods (property calculations, validation)
- API serializers and views
- Form validation logic
- Utility functions and helpers

**DON'T obsess over**:

- Django admin configuration
- Database migrations
- Settings files
- Simple getters/setters
- `__repr__` / `__str__` methods (unless critical)

### Handling Uncovered Code

If coverage drops below 80%:

1. **Add missing tests**: Focus on critical business logic first
2. **Refactor untestable code**: Extract pure functions from side effects
3. **Document why**: If code is intentionally untested (e.g., legacy), add `# pragma: no cover`

```python
def legacy_import_function():
    """Old import format - deprecated, will be removed in v2.0."""
    # pragma: no cover
    # This code is untested and scheduled for removal
    pass
```

---

## Related Documentation

- [Test Organization Guide](../../tests/README.md)
- [Test Fixtures Reference](../../tests/fixtures/README.md)
- [Contributing Guidelines](../../CONTRIBUTING.md)

---

**Questions?** See the [Testing FAQ](../testing-faq.md) or ask in `#testing` Slack channel.
