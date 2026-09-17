"""Tests for review.urls (T014, plan.md "The pages").

review-list's production wiring landed in T011's commit, because the
list view's own access-control tests need a resolvable URL to exercise
through the test client (see T011's completion notes). This is T014's own
confirming test: the route resolves by name, at the path plan.md's access
table gives the assessment list.
"""

import inspect

import pytest
from django.urls import resolve, reverse

from review import urls as review_urls
from review.views import (
    ReviewConfirmView,
    ReviewCreateView,
    ReviewDecideView,
    ReviewDetailView,
    ReviewListView,
    ReviewUpdateView,
    ReviewUploadView,
)


@pytest.mark.review
class TestReviewListRoute:
    def test_review_list_resolves_by_name_to_the_documented_path(self):
        assert reverse("review-list") == "/assessments/"

    def test_the_path_resolves_to_the_list_view(self):
        match = resolve("/assessments/")

        assert match.func.view_class is ReviewListView


@pytest.mark.review
class TestReviewCreateRoute:
    """T019: the description route resolves by the name plan.md's access
    table gives it."""

    def test_review_create_resolves_by_name_to_the_documented_path(self):
        assert reverse("review-create") == "/assessments/new/"

    def test_the_path_resolves_to_the_create_view(self):
        match = resolve("/assessments/new/")

        assert match.func.view_class is ReviewCreateView


@pytest.mark.review
class TestReviewDetailRoute:
    """T046, plan.md's access table: an assessment's own page."""

    def test_review_detail_resolves_by_name_to_the_documented_path(self):
        assert reverse("review-detail", kwargs={"pk": 1}) == "/assessments/1/"

    def test_the_path_resolves_to_the_detail_view(self):
        match = resolve("/assessments/1/")

        assert match.func.view_class is ReviewDetailView


@pytest.mark.review
class TestReviewUpdateRoute:
    """T047, plan.md's access table: correcting an assessment."""

    def test_review_update_resolves_by_name_to_the_documented_path(self):
        assert reverse("review-update", kwargs={"pk": 1}) == "/assessments/1/edit/"

    def test_the_path_resolves_to_the_update_view(self):
        match = resolve("/assessments/1/edit/")

        assert match.func.view_class is ReviewUpdateView


@pytest.mark.django_db
@pytest.mark.review
class TestTheDecisionQueueHasNoRouteOfItsOwn:
    """The waiting list is the assessment list narrowed to one state
    (FR-025), so it is a filter rather than a page. Asserted rather than
    merely deleted: a route quietly reinstated would leave two ways to ask
    the same question, one of which nothing maintains."""

    def test_no_route_is_registered_under_that_name(self):
        from django.urls import NoReverseMatch

        with pytest.raises(NoReverseMatch):
            reverse("review-queue")

    def test_the_narrowed_list_is_reachable_instead(self, client):
        from review.states import States

        response = client.get(
            reverse("review-list"), {"state": States.AWAITING_DECISION.value}
        )

        assert response.status_code == 200


@pytest.mark.review
class TestReviewDecideRoute:
    """T037, plan.md's access table: the decide route resolves by the name
    plan.md's access table gives it."""

    def test_review_decide_resolves_by_name_to_the_documented_path(self):
        assert reverse("review-decide", kwargs={"pk": 1}) == "/assessments/1/decide/"

    def test_the_path_resolves_to_the_decide_view(self):
        match = resolve("/assessments/1/decide/")

        assert match.func.view_class is ReviewDecideView


@pytest.mark.review
class TestNoRouteWritesWithoutChecking:
    """T024, spec.md SC-002, decisions.md D5: every route registered in
    ``review.urls`` is proven to reach a checked import through
    ``import_ghfdb_template`` — the one function that always validates
    before it writes — rather than the underlying GHFDB import resources
    directly. A view that re-implemented the write without going through it
    would pass every other test in this story and still violate SC-002, so
    this test inspects the route table's own view classes rather than one
    view's behaviour.

    Verified as a real guard, not a tautology (T024's own instruction):
    temporarily reinstating a bypass — a view calling
    ``GHFDBParentImportResource().import_data(...)`` directly instead of
    going through ``import_ghfdb_template`` — makes
    ``test_every_routed_view_avoids_the_import_resources_directly`` fail.
    """

    #: Symbols that write GHFDB rows directly. A view referencing one of
    #: these, rather than calling ``import_ghfdb_template``, writes without
    #: the check FR-008 requires.
    _WRITE_CAPABLE_SYMBOLS = (
        "GHFDBParentImportResource",
        "GHFDBChildImportResource",
        "import_data(",
    )

    def _routed_view_classes(self):
        for pattern in review_urls.urlpatterns:
            view_class = getattr(pattern.callback, "view_class", None)
            if view_class is not None:
                yield pattern.pattern, view_class

    def test_every_routed_view_avoids_the_import_resources_directly(self):
        for pattern, view_class in self._routed_view_classes():
            source = inspect.getsource(view_class)
            for symbol in self._WRITE_CAPABLE_SYMBOLS:
                assert symbol not in source, (
                    f"{view_class.__name__} (route {pattern}) references "
                    f"{symbol} directly, bypassing import_ghfdb_template's check."
                )

    def test_the_confirm_route_is_the_only_one_that_writes_for_real(self):
        confirm_source = inspect.getsource(ReviewConfirmView)
        upload_source = inspect.getsource(ReviewUploadView)

        assert "import_ghfdb_template" in confirm_source
        assert "check_only=False" in confirm_source

        assert "import_ghfdb_template" in upload_source
        assert "check_only=True" in upload_source
        assert "check_only=False" not in upload_source
