"""
Script to create Django JSON test fixtures for the GHFDB testing infrastructure.
These fixtures represent workflow states for testing the review and approval processes.
"""

import json
from datetime import datetime
from pathlib import Path

# Define the base path for fixtures
FIXTURES_DIR = Path(__file__).parent.parent / "tests" / "fixtures"
FIXTURES_DIR.mkdir(exist_ok=True)


def create_review_submission_fixture():
    """
    Create review_submission_dataset.json: Dataset in 'pending review' state.

    Represents a complete dataset submission with provenance metadata,
    awaiting admin/reviewer approval.
    """

    # Base date for consistent timestamps
    submission_date = datetime(2025, 7, 10, 14, 30, 0)

    fixture_data = [
        # Project
        {
            "model": "project.project",
            "pk": 100,
            "fields": {
                "uuid": "pTEST001ReviewSubmission",
                "name": "Test Review Project",
                "added": submission_date.isoformat() + "Z",
                "modified": submission_date.isoformat() + "Z",
                "visibility": 1,
                "status": 1,  # Active
            },
        },
        # Dataset - Pending Review State
        {
            "model": "dataset.dataset",
            "pk": 100,
            "fields": {
                "uuid": "dTEST001PendingReview",
                "name": "Test Submission - Pending Review",
                "added": submission_date.isoformat() + "Z",
                "modified": submission_date.isoformat() + "Z",
                "visibility": 0,  # Private - not yet published
                "project": 100,
                "reference": None,
            },
        },
        # Dataset Description - Abstract
        {
            "model": "dataset.datasetdescription",
            "pk": 100,
            "fields": {
                "type": "Abstract",
                "value": "This is a test dataset submitted for review. It contains heat flow measurements from a test drilling campaign conducted for quality assurance testing purposes.",
                "related": 100,
            },
        },
        # Dataset Description - Methods
        {
            "model": "dataset.datasetdescription",
            "pk": 101,
            "fields": {
                "type": "Methods",
                "value": "Heat flow measurements were obtained using standard borehole temperature logging and thermal conductivity measurements following IHFC guidelines.",
                "related": 100,
            },
        },
        # Dataset Dates
        {
            "model": "dataset.datasetdate",
            "pk": 100,
            "fields": {"type": "Submitted", "value": submission_date.strftime("%Y-%m-%d"), "related": 100},
        },
        {
            "model": "dataset.datasetdate",
            "pk": 101,
            "fields": {"type": "CollectionStart", "value": "2025-01-15", "related": 100},
        },
        {
            "model": "dataset.datasetdate",
            "pk": 102,
            "fields": {"type": "CollectionEnd", "value": "2025-03-20", "related": 100},
        },
    ]

    output_path = FIXTURES_DIR / "review_submission_dataset.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(fixture_data, f, indent=2, ensure_ascii=False)
    print(f"Created: {output_path}")
    return output_path


def create_admin_approval_fixture():
    """
    Create admin_approval_dataset.json: Dataset in 'reviewed/approved' state.

    Represents a complete dataset that has been reviewed and approved,
    including Review object with reviewer comments.
    """

    # Base dates
    submission_date = datetime(2025, 6, 1, 10, 0, 0)
    review_start = datetime(2025, 6, 5, 9, 0, 0)
    review_complete = datetime(2025, 6, 15, 16, 30, 0)

    fixture_data = [
        # Project
        {
            "model": "project.project",
            "pk": 200,
            "fields": {
                "uuid": "pTEST002ApprovedDataset",
                "name": "Test Approved Project",
                "added": submission_date.isoformat() + "Z",
                "modified": review_complete.isoformat() + "Z",
                "visibility": 1,
                "status": 3,  # Completed
            },
        },
        # Dataset - Approved/Published State
        {
            "model": "dataset.dataset",
            "pk": 200,
            "fields": {
                "uuid": "dTEST002ApprovedPublished",
                "name": "Test Dataset - Approved and Published",
                "added": submission_date.isoformat() + "Z",
                "modified": review_complete.isoformat() + "Z",
                "visibility": 1,  # Public - published
                "project": 200,
                "reference": None,
            },
        },
        # Dataset Description - Abstract
        {
            "model": "dataset.datasetdescription",
            "pk": 200,
            "fields": {
                "type": "Abstract",
                "value": "This test dataset has been reviewed and approved. It represents heat flow data that has passed quality control and is ready for publication in the Global Heat Flow Database.",
                "related": 200,
            },
        },
        # Dataset Description - Methods
        {
            "model": "dataset.datasetdescription",
            "pk": 201,
            "fields": {
                "type": "Methods",
                "value": "All measurements were conducted following IHFC standards. Quality scores (M-score and U-score) were calculated according to Fuchs et al. (2023). Data underwent rigorous QA/QC including validation of coordinates, depth intervals, and thermal conductivity values.",
                "related": 200,
            },
        },
        # Dataset Description - Technical Info
        {
            "model": "dataset.datasetdescription",
            "pk": 202,
            "fields": {
                "type": "TechnicalInfo",
                "value": "Dataset format: GHFDB v2.0 template. All mandatory fields completed. Includes provenance metadata with DOI references and contributor ORCID identifiers.",
                "related": 200,
            },
        },
        # Dataset Dates
        {
            "model": "dataset.datasetdate",
            "pk": 200,
            "fields": {"type": "Submitted", "value": submission_date.strftime("%Y-%m-%d"), "related": 200},
        },
        {
            "model": "dataset.datasetdate",
            "pk": 201,
            "fields": {"type": "Available", "value": review_complete.strftime("%Y-%m-%d"), "related": 200},
        },
        {
            "model": "dataset.datasetdate",
            "pk": 202,
            "fields": {"type": "CollectionStart", "value": "2024-09-01", "related": 200},
        },
        {
            "model": "dataset.datasetdate",
            "pk": 203,
            "fields": {"type": "CollectionEnd", "value": "2024-11-30", "related": 200},
        },
        # Review Object - Complete
        {
            "model": "review.review",
            "pk": 200,
            "fields": {
                "dataset": 200,
                "literature": None,
                "start_date": review_start.strftime("%Y-%m-%d"),
                "end_date": review_complete.strftime("%Y-%m-%d"),
                "status": 2,  # COMPLETE
                "comment": "Dataset reviewed and approved. All quality checks passed. Coordinates validated against known site locations. Thermal conductivity values are within expected ranges for reported lithologies. Measurement methods are well-documented. Recommended for publication in GHFDB.",
            },
        },
    ]

    output_path = FIXTURES_DIR / "admin_approval_dataset.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(fixture_data, f, indent=2, ensure_ascii=False)
    print(f"Created: {output_path}")
    return output_path


def create_round_trip_fixture():
    """
    Create round_trip_reference.xlsx: Comprehensive fixture with 10 sites.

    This would be an Excel file, but we'll create the specification here.
    The actual Excel creation will use openpyxl similar to the minimal fixture.
    """
    # This would be implemented similar to create_minimal_fixture()
    # but with 10 sites covering all field types and vocabularies
    pass


if __name__ == "__main__":
    print("Creating Django JSON test fixtures...")
    print("=" * 60)

    # Create JSON fixtures
    create_review_submission_fixture()
    create_admin_approval_fixture()

    print("=" * 60)
    print("JSON fixture creation complete!")
    print("\nNote: Round-trip Excel fixture requires separate implementation")
    print("with comprehensive field coverage for export/import testing.")
