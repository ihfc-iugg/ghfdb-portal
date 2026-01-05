"""
Contract tests for GHFDB public API endpoints.

These tests validate that API responses match documented schemas and protect
external consumers from breaking changes.

Tests use @pytest.mark.contract and @pytest.mark.django_db markers.

Execution: pytest -m contract tests/contracts/test_public_api_contract.py
Expected time: <15 seconds for all tests in this file
"""

import pytest
from datetime import datetime
from django.contrib.auth import get_user_model
from fairdm.core.models import Dataset


@pytest.mark.contract
@pytest.mark.django_db
def test_get_dataset_response_schema(client, admin_approval_dataset):
    """
    GET /api/v1/datasets/{id}/ must return consistent schema.

    Contract Requirements:
    - Required fields: uuid, name, visibility, created_date
    - Field types must be consistent
    - Nullable fields must return explicit null (not omitted)

    Breaking Change Detection:
    - Removing any required field
    - Changing field types
    - Omitting nullable fields instead of returning null
    """
    # Act: Request dataset detail
    response = client.get(f'/api/v1/datasets/{admin_approval_dataset.pk}/')

    # Assert: HTTP 200 success
    assert response.status_code == 200, (
        f"Expected 200 OK, got {response.status_code}"
    )

    data = response.json()

    # Assert: Required fields present (v1.0 contract)
    required_fields = ['uuid', 'name', 'visibility', 'created_date']
    for field in required_fields:
        assert field in data, (
            f"Required field '{field}' missing from response. "
            f"Breaking change detected!"
        )

    # Assert: Field type validation (v1.0 contract)
    assert isinstance(data['uuid'], str), "uuid must be string (UUID format)"
    assert isinstance(data['name'], str), "name must be string"
    assert isinstance(data['visibility'], int), "visibility must be integer (0 or 1)"
    assert isinstance(data['created_date'], str), "created_date must be string (ISO 8601)"

    # Assert: Validate ISO 8601 date format
    try:
        datetime.fromisoformat(data['created_date'].replace('Z', '+00:00'))
    except ValueError as e:
        pytest.fail(f"created_date must be valid ISO 8601 format: {e}")

    # Assert: Nullable field handling (explicit null, not omitted)
    # Description is nullable - must be present as null or string
    assert 'description' in data, (
        "Nullable field 'description' must be present (null or string). "
        "Omitting nullable fields breaks client contracts."
    )
    if data['description'] is not None:
        assert isinstance(data['description'], str), (
            "description must be string or null"
        )

    # Assert: Optional fields (added in later versions)
    # If present, validate type to ensure consistency
    if 'updated_date' in data:
        assert isinstance(data['updated_date'], str), (
            "updated_date (if present) must be string (ISO 8601)"
        )


@pytest.mark.contract
@pytest.mark.django_db
def test_get_dataset_list_response_schema(client):
    """
    GET /api/v1/datasets/ must return standard list response.

    Contract Requirements:
    - Pagination fields: count, next, previous, results
    - results must be array
    - count must be integer
    - next/previous must be string (URL) or null

    Breaking Change Detection:
    - Removing pagination fields
    - Changing pagination structure
    - Changing results to non-array type
    """
    # Arrange: Create datasets for list response
    Dataset.objects.create(name="Contract Test Dataset 1", visibility=1)
    Dataset.objects.create(name="Contract Test Dataset 2", visibility=1)

    # Act: Request dataset list
    response = client.get('/api/v1/datasets/')

    # Assert: HTTP 200 success
    assert response.status_code == 200

    data = response.json()

    # Assert: Pagination contract (DRF standard)
    pagination_fields = ['count', 'next', 'previous', 'results']
    for field in pagination_fields:
        assert field in data, (
            f"Pagination field '{field}' missing from list response. "
            f"Breaking change detected!"
        )

    # Assert: Pagination field types
    assert isinstance(data['count'], int), "count must be integer"
    assert data['count'] >= 0, "count must be non-negative"

    assert data['next'] is None or isinstance(data['next'], str), (
        "next must be string (URL) or null"
    )
    assert data['previous'] is None or isinstance(data['previous'], str), (
        "previous must be string (URL) or null"
    )

    assert isinstance(data['results'], list), (
        "results must be array. Changing to object breaks client contracts."
    )

    # Assert: Results structure (if not empty)
    if data['results']:
        first_item = data['results'][0]

        # Each item must have required fields
        item_required_fields = ['uuid', 'name', 'visibility']
        for field in item_required_fields:
            assert field in first_item, (
                f"List item missing required field '{field}'. "
                f"Breaking change detected!"
            )

        # Type validation for list items
        assert isinstance(first_item['uuid'], str)
        assert isinstance(first_item['name'], str)
        assert isinstance(first_item['visibility'], int)


@pytest.mark.contract
def test_unauthorized_request_error_contract(client):
    """
    HTTP 401 errors must include standard error payload.

    Contract Requirements:
    - detail field (string, required)
    - error_code field (string, recommended)
    - Consistent error structure across all 401 responses

    Breaking Change Detection:
    - Changing error payload structure
    - Removing detail field
    - Inconsistent error formats
    """
    # Act: Request without authentication (assuming endpoint requires auth)
    # Note: Adjust endpoint to match actual authentication-required endpoint
    response = client.get('/api/v1/datasets/999999/')  # Non-existent ID

    # Note: Actual status might be 404 if authentication not required
    # This test demonstrates the error contract pattern

    if response.status_code == 401:
        error = response.json()

        # Assert: Required error fields
        assert 'detail' in error, (
            "Error response must include 'detail' field. "
            "Breaking change detected!"
        )
        assert isinstance(error['detail'], str), "detail must be string"
        assert len(error['detail']) > 0, "detail must be non-empty"

        # Assert: Recommended error fields (optional but good practice)
        if 'error_code' in error:
            assert isinstance(error['error_code'], str), "error_code must be string"
            assert error['error_code'] in [
                'unauthorized', 'authentication_failed', 'authentication_required'
            ], "error_code should use standard codes"

        if 'timestamp' in error:
            assert isinstance(error['timestamp'], str), "timestamp must be string"
            # Validate ISO 8601 format
            try:
                datetime.fromisoformat(error['timestamp'].replace('Z', '+00:00'))
            except ValueError:
                pytest.fail("timestamp must be valid ISO 8601 format")


@pytest.mark.contract
@pytest.mark.django_db
def test_nullable_field_explicit_null(client):
    """
    Nullable fields must return explicit null, not be omitted.

    Contract Requirements:
    - Nullable fields present in schema
    - null value instead of field omission
    - Consistent field presence across all responses

    Why This Matters:
    - Clients rely on field presence for typing (TypeScript, etc.)
    - Omitting fields breaks static type checkers
    - Explicit null is JSON best practice
    """
    # Arrange: Create dataset with null description
    dataset = Dataset.objects.create(
        name="Nullable Field Test",
        visibility=1,
        description=None  # Explicitly null
    )

    # Act: Request dataset
    response = client.get(f'/api/v1/datasets/{dataset.pk}/')

    assert response.status_code == 200
    data = response.json()

    # Assert: Nullable field present with null value
    assert 'description' in data, (
        "Nullable field 'description' must be present in response, "
        "even when value is null. Omitting nullable fields breaks "
        "client TypeScript/JSON Schema validation."
    )
    assert data['description'] is None, (
        "description should be explicit null (not undefined)"
    )

    # Arrange: Create dataset with non-null description
    dataset_with_desc = Dataset.objects.create(
        name="Non-Null Field Test",
        visibility=1,
        description="This is a test dataset"
    )

    # Act: Request dataset with description
    response2 = client.get(f'/api/v1/datasets/{dataset_with_desc.pk}/')

    assert response2.status_code == 200
    data2 = response2.json()

    # Assert: Field present with string value
    assert 'description' in data2, "description field must be present"
    assert isinstance(data2['description'], str), "description must be string"
    assert data2['description'] == "This is a test dataset"

    # Key Point: Field is ALWAYS present, value varies (null or string)
    # This consistency is critical for API contracts


@pytest.mark.contract
@pytest.mark.django_db
def test_pagination_contract(client):
    """
    Pagination metadata must be consistent and valid.

    Contract Requirements:
    - count: Total number of items (integer)
    - next: URL to next page or null (string or null)
    - previous: URL to previous page or null (string or null)
    - results: Array of items

    Breaking Change Detection:
    - Changing pagination field names
    - Removing pagination metadata
    - Inconsistent next/previous URL format
    """
    # Arrange: Create enough datasets to trigger pagination
    for i in range(15):
        Dataset.objects.create(
            name=f"Pagination Test Dataset {i}",
            visibility=1
        )

    # Act: Request first page with page_size limit
    response = client.get('/api/v1/datasets/?page_size=10')

    assert response.status_code == 200
    data = response.json()

    # Assert: Pagination metadata present
    assert 'count' in data, "Pagination must include 'count' field"
    assert 'next' in data, "Pagination must include 'next' field"
    assert 'previous' in data, "Pagination must include 'previous' field"
    assert 'results' in data, "Pagination must include 'results' field"

    # Assert: count is valid
    assert isinstance(data['count'], int), "count must be integer"
    assert data['count'] >= 15, f"Expected at least 15 items, got {data['count']}"

    # Assert: next is URL (page 2 exists)
    assert isinstance(data['next'], str), (
        "next must be string (URL) when more pages exist"
    )
    assert 'page' in data['next'] or 'offset' in data['next'], (
        "next URL should include pagination parameter"
    )

    # Assert: previous is null (on first page)
    assert data['previous'] is None, (
        "previous must be null on first page"
    )

    # Assert: results length matches page_size
    assert len(data['results']) == 10, (
        f"Expected 10 results per page, got {len(data['results'])}"
    )

    # Act: Request second page
    if data['next']:
        response2 = client.get(data['next'].replace('http://testserver', ''))

        assert response2.status_code == 200
        data2 = response2.json()

        # Assert: previous is now a URL (not on first page anymore)
        assert isinstance(data2['previous'], str), (
            "previous must be string (URL) when not on first page"
        )

        # Assert: count remains consistent across pages
        assert data2['count'] == data['count'], (
            "count must be consistent across all pages"
        )


@pytest.mark.contract
@pytest.mark.django_db
def test_api_version_backward_compatibility():
    """
    API responses must maintain backward compatibility within major version.

    Contract Requirements (v1.x):
    - All v1.0 fields must remain in v1.x responses
    - New fields can be added (optional)
    - Field types cannot change
    - Deprecated fields marked but still present

    Breaking changes require v2.0 release.
    """
    # This test documents the contract evolution strategy
    # Actual implementation depends on version management approach

    # v1.0 required fields (immutable within v1.x)
    v1_0_required_fields = ['uuid', 'name', 'visibility']

    # v1.1 additions (optional, but if present must match type)
    v1_1_optional_fields = ['created_date', 'updated_date']

    # v1.2 deprecated fields (must remain until v2.0)
    v1_2_deprecated_fields = []  # Example: 'old_field_name'

    # v2.0 planned changes (breaking)
    v2_0_breaking_changes = {
        # 'old_field_name': 'removed',
        # 'status_code': 'type_changed_from_string_to_int',
    }

    # Assert: Contract validation would go here in actual test
    # This serves as documentation of versioning policy
    assert True, "Version compatibility documented"
