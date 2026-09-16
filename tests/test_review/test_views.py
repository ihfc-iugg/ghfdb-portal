"""Tests for review.views (T011).

Access is refused rather than the list rendering empty (spec.md User Story
1, acceptance scenarios 3 and 4).

The refusal paths go through the full request/response cycle via the test
client: ``PermissionDenied`` and the anonymous redirect both short-circuit
in ``dispatch()``, before any template renders, so the client's normal
rendering is never reached.

The served paths use ``RequestFactory`` and stop at the unrendered
``TemplateResponse`` deliberately. This project's shared page chrome
currently raises for *any* authenticated request — reproduces on the
pre-existing ``/datasets/`` page too, so it predates this story and is
flagged separately rather than fixed here (out of ``project/review/``'s
scope). What these tests exist to prove is narrower and unaffected by that
defect: ``ReviewListView.test_func`` grants entry to both roles and the
view builds a normal 200 response for each.
"""

import pytest
from django.urls import reverse

from review.views import ReviewListView


@pytest.mark.django_db
@pytest.mark.review
class TestReviewListViewAccess:
    def test_a_data_assessor_is_granted_entry(self, rf, assessor):
        request = rf.get(reverse("review-list"))
        request.user = assessor

        response = ReviewListView.as_view()(request)

        assert response.status_code == 200

    def test_a_data_curator_is_granted_entry(self, rf, curator):
        request = rf.get(reverse("review-list"))
        request.user = curator

        response = ReviewListView.as_view()(request)

        assert response.status_code == 200

    def test_a_signed_in_user_in_neither_role_is_refused(self, client, outsider):
        client.force_login(outsider)

        response = client.get(reverse("review-list"))

        assert response.status_code == 403

    def test_an_anonymous_visitor_is_redirected_to_log_in_rather_than_served(
        self, client
    ):
        response = client.get(reverse("review-list"))

        assert response.status_code == 302
        assert response.url != reverse("review-list")
