"""Tests for review.menus (T013, plan.md "Notification").

Visibility is tested against ``check()`` directly rather than a full page
render, which is the one hook the request reaches and so the whole of what
the item decides — who sees it, and what count it carries for a curator.
"""

import pytest
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from easy_icons import icon
from fairdm.menus import AppMenu
from review.menus import (
    assessment_entry,
    assessment_group,
    awaiting_decision_entry,
)
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

    def test_both_entries_sit_under_the_data_assessment_heading(self):
        assert assessment_entry.parent is assessment_group
        assert awaiting_decision_entry.parent is assessment_group
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
    """The entry leads to a public page, so everyone sees it. Hiding it
    would leave that page reachable only by typing its URL."""

    def test_visible_to_a_data_assessor(self, rf, assessor):
        request = rf.get("/")
        request.user = assessor

        assert assessment_entry.check(request) is True

    def test_visible_to_a_data_curator(self, rf, curator):
        request = rf.get("/")
        request.user = curator

        assert assessment_entry.check(request) is True

    def test_visible_to_a_user_in_neither_role(self, rf, outsider):
        request = rf.get("/")
        request.user = outsider

        assert assessment_entry.check(request) is True

    def test_visible_to_an_anonymous_visitor(self, rf):
        request = rf.get("/")
        request.user = AnonymousUser()

        assert assessment_entry.check(request) is True

    def test_visible_on_a_request_that_carries_no_user(self, rf):
        """A request from outside the auth middleware, such as an error page
        rendered before it ran."""
        assert assessment_entry.check(rf.get("/")) is True


@pytest.mark.django_db
@pytest.mark.review
class TestAwaitingDecisionEntry:
    """The curator's own entry: what is waiting, and how many (FR-022)."""

    def test_visible_to_a_data_curator(self, rf, curator):
        request = rf.get("/")
        request.user = curator

        assert awaiting_decision_entry.check(request) is True

    def test_hidden_from_a_data_assessor(self, rf, assessor):
        request = rf.get("/")
        request.user = assessor

        assert awaiting_decision_entry.check(request) is False

    def test_hidden_from_an_anonymous_visitor(self, rf):
        request = rf.get("/")
        request.user = AnonymousUser()

        assert awaiting_decision_entry.check(request) is False

    def test_carries_the_count_awaiting_decision(self, rf, curator):
        ReviewFactory(state=States.AWAITING_DECISION)
        ReviewFactory(state=States.AWAITING_DECISION)
        ReviewFactory(state=States.DESCRIBED)
        request = rf.get("/")
        request.user = curator

        awaiting_decision_entry.check(request)

        assert awaiting_decision_entry.extra_context["badge"] == 2

    def test_the_count_follows_the_data_rather_than_being_written_once(
        self, rf, curator
    ):
        """The item is a module-level singleton reused across every request,
        so a count computed once at import would be permanently stale."""
        request = rf.get("/")
        request.user = curator
        awaiting_decision_entry.check(request)
        assert awaiting_decision_entry.extra_context["badge"] == 0

        ReviewFactory(state=States.AWAITING_DECISION)

        awaiting_decision_entry.check(request)

        assert awaiting_decision_entry.extra_context["badge"] == 1

    def test_it_leads_to_the_list_narrowed_to_what_is_waiting(self, rf, curator):
        request = rf.get("/")
        request.user = curator
        awaiting_decision_entry.check(request)

        url = awaiting_decision_entry.resolve_url()

        assert url == f"{reverse('review-list')}?state={States.AWAITING_DECISION.value}"

    def test_the_plain_entry_carries_no_count(self, rf, curator):
        ReviewFactory(state=States.AWAITING_DECISION)
        request = rf.get("/")
        request.user = curator

        assessment_entry.check(request)

        assert "badge" not in assessment_entry.extra_context
