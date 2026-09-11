"""
Shared fixtures for test_ghfdb/test_resources.

Provides the ``dataset`` fixture, re-exported from the parent conftest. The
vocabulary concepts these tests read are written once for the session, in
``tests/conftest.py``.
"""

from pathlib import Path

import openpyxl
import pytest
from fairdm.factories import DatasetFactory


@pytest.fixture
def dataset(db):
    """A minimal FairDM Dataset — infrastructure, not under test."""
    return DatasetFactory()


@pytest.fixture
def official_upload_template_workbook():
    """The official GHFDB upload template, opened unmodified (US-1, T001).

    ``tests/fixtures/official_upload_template.xlsx`` is a byte-identical copy
    of ``docs/constitution/references/data_upload_template.xlsx``.
    """
    path = (
        Path(__file__).resolve().parents[2]
        / "fixtures"
        / "official_upload_template.xlsx"
    )
    return openpyxl.load_workbook(path, data_only=True)
