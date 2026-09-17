"""Tests for review.menus (T013, plan.md "Notification").

Visibility is tested against ``check()`` directly rather than a full page
render, which is the one hook the request reaches and so the whole of what
the item decides — who sees it, and what count it carries for a curator.
"""

import pytest
from django.contrib.auth.models import AnonymousUser
from easy_icons import icon
from fairdm.menus import AppMenu

from review.menus import assessment_entry, assessment_group
from review.states import States
from tests.test_review.factories import ReviewFactory


@pytest.mark.review
class TestAssessmentGroupPlacement:
    """T042: the entry sits under a heading of its own, immediately before
    Community, rather than appended to the end of the navigation where it
    fell under whichever heading came last.

    Asserted against the assembled tree: the position is worked out at
    import time from what the framework and this project have each added,
    so a number written into the test would prove only that the number had
    been copied.
    """

    def test_the_entry_sits_under_the_data_assessment_heading(self):
        assert assessment_entry.parent is assessment_group
        assert str(assessment_group.name) == "Data Assessment"

    def test_the_heading_comes_directly_before_community(self):
        names = [str(child.name) for child in AppMenu.children]

        assert names.index("Data Assessment") == names.index("Community") - 1

    def test_the_entry_carries_a_label_and_an_icon_that_draws(self):
        assert str(assessment_entry.extra_context["label"]) == "Data Assessments"
        assert icon(assessment_entry.extra_context["icon"])


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
