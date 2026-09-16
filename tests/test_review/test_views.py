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
from django.template.loader import render_to_string
from django.urls import reverse

from review.states import States
from review.views import ReviewListView
from tests.test_review.factories import ReviewFactory


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


@pytest.mark.django_db
@pytest.mark.review
class TestReviewListItemTemplate:
    """T012: each row names the publication it covers, its uploader and its
    state (spec.md User Story 1, acceptance scenario 5), asserted against
    the rendered HTML rather than the template context.

    Rendered directly rather than through the full list page: the page
    chrome around it is affected by the pre-existing defect noted on
    ReviewListView's tests above, and this is what T012 owns.
    """

    def test_row_names_the_publication_uploader_and_state(self, assessor):
        review = ReviewFactory(
            uploaded_by=assessor,
            state=States.AWAITING_DECISION,
        )

        html = render_to_string(
            "review/review_list_item.html", {"review": review, "object": review}
        )

        assert str(review.literature) in html
        assert str(assessor) in html
        assert review.get_state_display() in html
