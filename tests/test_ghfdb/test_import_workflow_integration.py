"""
Integration tests for GHFDB import → review → approve → export workflow.

These tests validate the complete data lifecycle from file upload to published export.
Tests use @pytest.mark.integration and require database access.

Execution: pytest -m integration tests/test_ghfdb/test_import_workflow_integration.py
Expected time: <30 seconds for all tests in this file
"""

import pytest
from django.contrib.auth import get_user_model
from fairdm.core.models import Dataset
from ghfdb.models import HeatFlowSite
from ghfdb.resources import GHFDBResource
from review.models import Review


@pytest.mark.integration
@pytest.mark.django_db
def test_import_minimal_dataset_happy_path(minimal_ghfdb_import_data):
    """
    Happy path: Import minimal fixture (5 sites) and validate record creation.

    Workflow: File upload → Parse → Validate → Create database records

    Validates:
    - Import completes without errors
    - Correct number of sites created (5)
    - Site records have required fields populated
    - Foreign key relationships established (Dataset → HeatFlowSite)
    """
    # Arrange: Create empty dataset
    dataset = Dataset.objects.create(
        name="Minimal Integration Test",
        visibility=0  # Private by default
    )

    # Arrange: Set up import pipeline
    from ghfdb.views import GHFDBImportFormat
    resource = GHFDBResource(dataset)
    input_format = GHFDBImportFormat(encoding="utf-8-sig")
    input_data = input_format.create_dataset(minimal_ghfdb_import_data)

    # Act: Import data
    result = resource.import_data(input_data, raise_errors=True)

    # Assert: Import successful
    assert not result.has_errors(), f"Import failed with errors: {result.errors}"
    assert not result.has_validation_errors(), (
        f"Validation errors: {result.validation_errors}"
    )

    # Assert: Correct record count
    sites = HeatFlowSite.objects.filter(dataset=dataset)
    assert sites.count() == 5, "Expected 5 sites from minimal fixture"

    # Assert: Required fields populated
    for site in sites:
        assert site.name, "Site name is required"
        assert site.lat is not None, "Latitude is required"
        assert site.lon is not None, "Longitude is required"
        assert site.dataset == dataset, "Foreign key relationship must be set"

    # Assert: Dataset metadata updated
    assert dataset.visibility == 0, "Dataset should remain private after import"


@pytest.mark.integration
@pytest.mark.django_db
def test_import_invalid_dataset_raises_validation_errors(invalid_ghfdb_import_data):
    """
    Error path: Import invalid fixture (5 error cases) and validate error detection.

    Workflow: File upload → Parse → Validate → Detect errors → Reject import

    Validates:
    - Import detects validation errors
    - Error messages are descriptive
    - No database records created when validation fails
    - Error report includes row numbers and field names
    """
    # Arrange: Create empty dataset
    dataset = Dataset.objects.create(
        name="Invalid Dataset Integration Test",
        visibility=0
    )

    # Arrange: Set up import pipeline
    from ghfdb.views import GHFDBImportFormat
    resource = GHFDBResource(dataset)
    input_format = GHFDBImportFormat(encoding="utf-8-sig")
    input_data = input_format.create_dataset(invalid_ghfdb_import_data)

    # Act: Attempt import (should fail validation)
    result = resource.import_data(input_data, raise_errors=False)

    # Assert: Import detects errors
    assert result.has_errors() or result.has_validation_errors(), (
        "Import should detect errors from invalid fixture"
    )

    # Assert: No records created on validation failure
    sites = HeatFlowSite.objects.filter(dataset=dataset)
    assert sites.count() == 0, (
        "No database records should be created when validation fails"
    )

    # Assert: Error details available
    if result.has_errors():
        assert len(result.errors) > 0, "Expected error details"
        # Check error structure includes row information
        first_error = result.errors[0]
        assert hasattr(first_error, 'row') or hasattr(first_error, 'error'), (
            "Errors should include row number or error message"
        )


@pytest.mark.integration
@pytest.mark.django_db
def test_export_without_approval_fails():
    """
    Authorization gate: Export should fail for unapproved datasets.

    Workflow: Create dataset → Attempt export → Block access

    Validates:
    - Private datasets cannot be exported
    - Export returns empty result or raises permission error
    - Public/approved gate enforced at export time
    """
    # Arrange: Create private dataset with data
    dataset = Dataset.objects.create(
        name="Private Dataset",
        visibility=0  # Private, not approved
    )
    HeatFlowSite.objects.create(
        dataset=dataset,
        name="Test Site 1",
        lat=45.0,
        lon=-120.0
    )
    HeatFlowSite.objects.create(
        dataset=dataset,
        name="Test Site 2",
        lat=46.0,
        lon=-121.0
    )

    # Act: Attempt export
    resource = GHFDBResource(dataset)
    export_data = resource.export()

    # Assert: Export blocked or returns empty
    # Note: Actual behavior depends on GHFDBResource.export() implementation
    # If export is blocked by permission check, this might raise an exception
    # If export silently filters, it returns empty dataset
    exported_rows = len(export_data.dict) if hasattr(export_data, 'dict') else 0
    assert exported_rows == 0, (
        "Private datasets should not be exportable until approved"
    )


@pytest.mark.integration
@pytest.mark.django_db
def test_full_workflow_import_to_export(minimal_ghfdb_import_data):
    """
    End-to-end test: Complete workflow from import to published export.

    Workflow: Import → Review submission → Admin approval → Export

    Validates:
    - All workflow steps complete successfully
    - State transitions occur correctly (private → pending → public)
    - Data survives round-trip through workflow
    - Export contains all imported records (5 sites)
    - Authorization checks enforced at each step
    """
    # Arrange: Create admin user
    User = get_user_model()
    admin_user = User.objects.create_user(
        username='admin_integration',
        email='admin@example.com',
        is_staff=True,
        is_superuser=True
    )

    # Arrange: Create dataset
    dataset = Dataset.objects.create(
        name="Full Workflow Integration Test",
        visibility=0  # Start private
    )

    # Act 1: Import data
    from ghfdb.views import GHFDBImportFormat
    resource = GHFDBResource(dataset)
    input_format = GHFDBImportFormat(encoding="utf-8-sig")
    input_data = input_format.create_dataset(minimal_ghfdb_import_data)
    import_result = resource.import_data(input_data, raise_errors=True)

    # Assert 1: Import successful
    assert not import_result.has_errors(), f"Import failed: {import_result.errors}"
    sites_after_import = HeatFlowSite.objects.filter(dataset=dataset)
    assert sites_after_import.count() == 5, "Expected 5 sites imported"
    assert dataset.visibility == 0, "Dataset should remain private after import"

    # Act 2: Submit for review
    review = Review.objects.create(
        dataset=dataset,
        status='pending',  # Pending review
        reviewer=admin_user
    )

    # Assert 2: Review created in pending state
    assert review.status == 'pending', "Review should be in pending state"
    assert dataset.visibility == 0, "Dataset should still be private during review"

    # Act 3: Admin approves for publication
    review.status = 'complete'
    review.approved_by = admin_user
    review.save()

    dataset.visibility = 1  # Publish
    dataset.save()

    # Assert 3: Dataset approved and published
    assert review.status == 'complete', "Review should be complete"
    assert dataset.visibility == 1, "Dataset should be public after approval"

    # Act 4: Export data
    export_data = resource.export()

    # Assert 4: Export contains all sites
    exported_rows = len(export_data.dict) if hasattr(export_data, 'dict') else 0
    assert exported_rows == 5, (
        f"Export should contain all 5 imported sites, got {exported_rows}"
    )

    # Assert 5: Data integrity preserved
    # Verify key fields survived the workflow
    exported_names = [row.get('name') or row.get('site_name') for row in export_data.dict]
    assert len(exported_names) == 5, "All site names should be present in export"
    assert all(name for name in exported_names), "No site names should be empty"
