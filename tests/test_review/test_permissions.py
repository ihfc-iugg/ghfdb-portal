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
    return Group.objects.get_or_create(name="Data Assessor")[0]


@pytest.fixture
def data_curator_group(db):
    return Group.objects.get_or_create(name="Data Curator")[0]


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
class TestCanManageUpload:
    """T020, plan.md "The pages": the upload and confirm routes are open to
    the assessment's own uploader, or to any Data Curator, and refused to
    everyone else — including a signed-in Data Assessor who did not create
    the assessment."""

    def test_the_uploader_may_manage_their_own_upload(self):
        from review.permissions import can_manage_upload

        from tests.test_review.factories import ReviewFactory

        uploader = ClaimedPersonFactory()
        review = ReviewFactory(uploaded_by=uploader)

        assert can_manage_upload(uploader, review) is True

    def test_any_curator_may_manage_an_upload_they_did_not_create(
        self, data_curator_group
    ):
        from review.permissions import can_manage_upload

        from tests.test_review.factories import ReviewFactory

        uploader = ClaimedPersonFactory()
        review = ReviewFactory(uploaded_by=uploader)
        curator = ClaimedPersonFactory()
        curator.groups.add(data_curator_group)

        assert can_manage_upload(curator, review) is True

    def test_a_different_assessor_may_not_manage_it(self, data_assessor_group):
        from review.permissions import can_manage_upload

        from tests.test_review.factories import ReviewFactory

        uploader = ClaimedPersonFactory()
        review = ReviewFactory(uploaded_by=uploader)
        other = ClaimedPersonFactory()
        other.groups.add(data_assessor_group)

        assert can_manage_upload(other, review) is False

    def test_an_anonymous_user_may_not_manage_it(self):
        from django.contrib.auth.models import AnonymousUser
        from review.permissions import can_manage_upload

        from tests.test_review.factories import ReviewFactory

        review = ReviewFactory()

        assert can_manage_upload(AnonymousUser(), review) is False


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


@pytest.mark.django_db
@pytest.mark.review
class TestIsAssessmentTeamMember:
    """Either role is on the team; nobody else is. The list, the description
    form and the navigation entry all ask this one question rather than
    testing the two roles in turn."""

    def test_true_for_a_data_assessor(self, data_assessor_group):
        from review.permissions import is_assessment_team_member

        person = ClaimedPersonFactory()
        person.groups.add(data_assessor_group)

        assert is_assessment_team_member(person) is True

    def test_true_for_a_data_curator(self, data_curator_group):
        from review.permissions import is_assessment_team_member

        person = ClaimedPersonFactory()
        person.groups.add(data_curator_group)

        assert is_assessment_team_member(person) is True

    def test_true_for_a_user_in_both_groups(
        self, data_assessor_group, data_curator_group
    ):
        from review.permissions import is_assessment_team_member

        person = ClaimedPersonFactory()
        person.groups.add(data_assessor_group, data_curator_group)

        assert is_assessment_team_member(person) is True

    def test_false_for_a_user_in_neither_group(self):
        from review.permissions import is_assessment_team_member

        person = ClaimedPersonFactory()

        assert is_assessment_team_member(person) is False

    def test_asks_the_database_once(
        self, data_assessor_group, django_assert_num_queries
    ):
        from review.permissions import is_assessment_team_member

        person = ClaimedPersonFactory()
        person.groups.add(data_assessor_group)

        with django_assert_num_queries(1):
            is_assessment_team_member(person)
