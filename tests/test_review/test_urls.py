"""Tests for review.urls (T014, plan.md "The pages").

review-list's production wiring landed in T011's commit, because the
list view's own access-control tests need a resolvable URL to exercise
through the test client (see T011's completion notes). This is T014's own
confirming test: the route resolves by name, at the path plan.md's access
table gives the assessment list.
"""

import pytest
from django.urls import resolve, reverse

from review.views import ReviewListView


@pytest.mark.review
class TestReviewListRoute:
    def test_review_list_resolves_by_name_to_the_documented_path(self):
        assert reverse("review-list") == "/assessments/"

    def test_the_path_resolves_to_the_list_view(self):
        match = resolve("/assessments/")

        assert match.func.view_class is ReviewListView
