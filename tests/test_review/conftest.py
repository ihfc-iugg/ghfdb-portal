"""Shared pytest fixtures for the test_review suite (Article VI)."""

import pytest
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from fairdm.factories import PersonFactory

from tests.test_ghfdb.test_importers import ROW, _build_official_xlsx


@pytest.fixture
def valid_upload_bytes() -> bytes:
    """The bytes of an official-template XLSX file carrying one clean row —
    the same row ``test_ghfdb.test_importers`` already proves imports
    without error, reused here rather than re-declared so the two suites
    cannot drift on what "a valid file" means (T020)."""
    headers = list(ROW.keys())
    return _build_official_xlsx(headers, [[ROW[header] for header in headers]])


@pytest.fixture
def valid_upload_file(valid_upload_bytes) -> SimpleUploadedFile:
    return SimpleUploadedFile(
        "assessment.xlsx",
        valid_upload_bytes,
        content_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
    )


@pytest.fixture
def data_assessor_group(db):
    return Group.objects.get_or_create(name="Data Assessor")[0]


@pytest.fixture
def data_curator_group(db):
    return Group.objects.get_or_create(name="Data Curator")[0]


@pytest.fixture
def claimed_person(db):
    """A person who has claimed their profile: a usable password and
    ``is_claimed=True``, unlike ``PersonFactory``'s own unclaimed default."""
    return PersonFactory(is_claimed=True, password="test-pass-123")


@pytest.fixture
def assessor(data_assessor_group):
    """A signed-in user in the Data Assessor group, and no other."""
    user = PersonFactory(is_claimed=True, password="test-pass-123")
    user.groups.add(data_assessor_group)
    return user


@pytest.fixture
def curator(data_curator_group):
    """A signed-in user in the Data Curator group, and no other."""
    user = PersonFactory(is_claimed=True, password="test-pass-123")
    user.groups.add(data_curator_group)
    return user


@pytest.fixture
def outsider(claimed_person):
    """A signed-in user in neither the Data Assessor nor Data Curator group."""
    return claimed_person
