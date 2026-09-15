"""Tests for review.permissions (T004).

``is_data_assessor``/``is_data_curator`` are the only place group membership
is tested — every view, navigation check and template condition is meant to
call these two functions rather than testing group names inline.
"""

import pytest
from django.contrib.auth.models import Group

from tests.test_review.factories import ClaimedPersonFactory


@pytest.fixture
def data_assessor_group(db):
    return Group.objects.create(name="Data Assessor")


@pytest.fixture
def data_curator_group(db):
    return Group.objects.create(name="Data Curator")


@pytest.mark.django_db
@pytest.mark.review
class TestIsDataAssessor:
    def test_true_for_a_user_in_the_data_assessor_group(self, data_assessor_group):
        from review.permissions import is_data_assessor

        person = ClaimedPersonFactory()
        person.groups.add(data_assessor_group)

        assert is_data_assessor(person) is True

    def test_false_for_a_user_in_neither_group(self):
        from review.permissions import is_data_assessor

        person = ClaimedPersonFactory()

        assert is_data_assessor(person) is False

    def test_true_for_a_user_in_both_groups(
        self, data_assessor_group, data_curator_group
    ):
        from review.permissions import is_data_assessor

        person = ClaimedPersonFactory()
        person.groups.add(data_assessor_group, data_curator_group)

        assert is_data_assessor(person) is True


@pytest.mark.django_db
@pytest.mark.review
class TestIsDataCurator:
    def test_true_for_a_user_in_the_data_curator_group(self, data_curator_group):
        from review.permissions import is_data_curator

        person = ClaimedPersonFactory()
        person.groups.add(data_curator_group)

        assert is_data_curator(person) is True

    def test_false_for_a_user_in_neither_group(self):
        from review.permissions import is_data_curator

        person = ClaimedPersonFactory()

        assert is_data_curator(person) is False

    def test_true_for_a_user_in_both_groups(
        self, data_assessor_group, data_curator_group
    ):
        from review.permissions import is_data_curator

        person = ClaimedPersonFactory()
        person.groups.add(data_assessor_group, data_curator_group)

        assert is_data_curator(person) is True
