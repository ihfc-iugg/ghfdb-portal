"""Shared pytest fixtures for the test_review suite (Article VI)."""

import pytest
from django.contrib.auth.models import Group

from tests.test_review.factories import ClaimedPersonFactory


@pytest.fixture
def data_assessor_group(db):
    return Group.objects.create(name="Data Assessor")


@pytest.fixture
def data_curator_group(db):
    return Group.objects.create(name="Data Curator")


@pytest.fixture
def assessor(data_assessor_group):
    """A signed-in user in the Data Assessor group, and no other."""
    user = ClaimedPersonFactory()
    user.groups.add(data_assessor_group)
    return user


@pytest.fixture
def curator(data_curator_group):
    """A signed-in user in the Data Curator group, and no other."""
    user = ClaimedPersonFactory()
    user.groups.add(data_curator_group)
    return user


@pytest.fixture
def outsider(db):
    """A signed-in user in neither the Data Assessor nor Data Curator group."""
    return ClaimedPersonFactory()
