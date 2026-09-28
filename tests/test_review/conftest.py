import pytest
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from fairdm.factories import PersonFactory

from tests.test_ghfdb.test_importers import ROW, _build_official_xlsx


@pytest.fixture
def valid_upload_bytes() -> bytes:
    # The bytes of an official-template XLSX file carrying one clean row — the same row
    # ``test_ghfdb.test_importers`` already proves imports without error.
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
    # A person who has claimed their profile: a usable password and ``is_claimed=True``,
    # unlike ``PersonFactory``'s own unclaimed default.
    return PersonFactory(is_claimed=True, password="test-pass-123")


@pytest.fixture
def assessor(data_assessor_group):
    user = PersonFactory(is_claimed=True, password="test-pass-123")
    user.groups.add(data_assessor_group)
    return user


@pytest.fixture
def curator(data_curator_group):
    user = PersonFactory(is_claimed=True, password="test-pass-123")
    user.groups.add(data_curator_group)
    return user


@pytest.fixture
def outsider(claimed_person):
    return claimed_person
