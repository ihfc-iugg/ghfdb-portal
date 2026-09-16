"""Tests for review.menus (T013, plan.md "Notification").

Tested against ``check()`` directly rather than a full page render: the
shared page chrome currently raises for any authenticated request (see
T011's completion notes), which is unrelated to and would mask what this
menu item itself is responsible for — who it is visible to, and what count
it carries for a curator.
"""

import pytest
from django.contrib.auth.models import AnonymousUser

from review.menus import assessment_entry
from review.states import States
from tests.test_review.factories import ReviewFactory


@pytest.mark.django_db
@pytest.mark.review
class TestAssessmentEntryVisibility:
    def test_visible_to_a_data_assessor(self, rf, assessor):
        request = rf.get("/")
        request.user = assessor

        assert assessment_entry.check(request) is True

    def test_visible_to_a_data_curator(self, rf, curator):
        request = rf.get("/")
        request.user = curator

        assert assessment_entry.check(request) is True

    def test_hidden_from_a_user_in_neither_role(self, rf, outsider):
        request = rf.get("/")
        request.user = outsider

        assert assessment_entry.check(request) is False

    def test_hidden_from_an_anonymous_visitor(self, rf):
        request = rf.get("/")
        request.user = AnonymousUser()

        assert assessment_entry.check(request) is False


@pytest.mark.django_db
@pytest.mark.review
class TestAssessmentEntryBadge:
    def test_carries_the_count_awaiting_decision_for_a_curator(self, rf, curator):
        ReviewFactory(state=States.AWAITING_DECISION)
        ReviewFactory(state=States.AWAITING_DECISION)
        ReviewFactory(state=States.DESCRIBED)
        request = rf.get("/")
        request.user = curator

        assessment_entry.check(request)

        assert assessment_entry.extra_context["badge"] == 2

    def test_carries_no_badge_for_an_assessor(self, rf, assessor):
        request = rf.get("/")
        request.user = assessor

        assessment_entry.check(request)

        assert "badge" not in assessment_entry.extra_context

    def test_a_later_check_for_an_assessor_clears_a_curators_earlier_badge(
        self, rf, curator, assessor
    ):
        """The item is a module-level singleton reused across requests, so a
        stale badge from one request must not survive into the next."""
        ReviewFactory(state=States.AWAITING_DECISION)
        curator_request = rf.get("/")
        curator_request.user = curator
        assessment_entry.check(curator_request)
        assert "badge" in assessment_entry.extra_context

        assessor_request = rf.get("/")
        assessor_request.user = assessor

        assessment_entry.check(assessor_request)

        assert "badge" not in assessment_entry.extra_context
