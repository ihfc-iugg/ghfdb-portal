import re

import pytest
from django.urls import reverse

from project.ghfdb.views import GHFDBParentTableView
from tests.conftest import requires_browser

from .test_tables import make_parent


class TestExplorePage:
    @pytest.mark.django_db
    def test_explore_page_is_public_and_returns_200(self, client):
        response = client.get(reverse("ghfdb-explore"))
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_explore_page_contains_visible_fallback_markup(self, client):
        response = client.get(reverse("ghfdb-explore"))
        content = response.content.decode("utf-8")
        assert 'id="map-error"' in content


VIEWPORTS = {
    "desktop": {"width": 1440, "height": 900},
    "mobile": {"width": 390, "height": 844},
}

at_every_viewport = pytest.mark.parametrize(
    "viewport", VIEWPORTS.values(), ids=list(VIEWPORTS)
)


def _layout(page, url, viewport):
    """Load the explore page at a viewport and report what the browser computed."""
    page.set_viewport_size(viewport)
    page.goto(url)
    return page.evaluate("""
        () => {
          const el = document.querySelector('iframe');
          const rect = el ? el.getBoundingClientRect() : null;
          return {
            viewport: window.innerHeight,
            documentHeight: document.documentElement.scrollHeight,
            mapHeight: rect ? Math.round(rect.height) : null,
          };
        }
    """)


@pytest.mark.e2e
@requires_browser
class TestExploreMapFillsTheShell:
    # The map viewer fills the shell on every device (issue #192). A rendered-HTML test
    # can only assert which classes are on which element.

    @at_every_viewport
    def test_the_map_never_computes_to_zero_height(self, page, live_server, viewport):
        # The failure mode #192 reports: the map renders into nothing on a phone.
        # iframe/Leaflet content measures its container once, so a container that
        # computes to zero shows nothing, with no error.
        layout = _layout(page, f"{live_server.url}/ghfdb/explore/", viewport)

        assert layout["mapHeight"] > 0, (
            "the map container resolved to zero height "
            f"in a {layout['viewport']}px viewport"
        )

    @at_every_viewport
    def test_the_map_fills_most_of_the_viewport(self, page, live_server, viewport):
        layout = _layout(page, f"{live_server.url}/ghfdb/explore/", viewport)

        assert layout["mapHeight"] > layout["viewport"] * 0.7, (
            f"map is {layout['mapHeight']}px in a {layout['viewport']}px "
            "viewport — the shell's height is not reaching it"
        )

    @at_every_viewport
    def test_the_window_does_not_scroll(self, page, live_server, viewport):
        layout = _layout(page, f"{live_server.url}/ghfdb/explore/", viewport)

        assert layout["documentHeight"] == layout["viewport"]


def listed_parents(response):
    """The published identifiers of the rows on the page, in order."""
    rows = re.findall(
        r"<tr[^>]*data-ghfdb=\"parent-row\"[^>]*>", response.content.decode()
    )
    return [int(re.search(r'data-parent="(\d+)"', row).group(1)) for row in rows]


@pytest.mark.django_db
class TestGHFDBParentTableView:
    def test_a_visitor_who_is_not_signed_in_sees_exactly_the_parents_served_to_them(
        self, client, published_dataset, unpublished_dataset
    ):
        from heat_flow.models import HeatFlowSite

        make_parent(published_dataset, 1)
        make_parent(unpublished_dataset, 2)
        hidden_site = make_parent(published_dataset, 3)
        HeatFlowSite.objects.filter(pk=hidden_site.sample_id).update(
            dataset=unpublished_dataset
        )

        response = client.get(reverse("ghfdb-parent-table"))

        assert response.status_code == 200
        assert listed_parents(response) == [1]

    def test_the_count_shown_is_the_number_of_parents_served(
        self, client, published_dataset, unpublished_dataset
    ):
        for ghfdb_id in (1, 2, 3):
            make_parent(published_dataset, ghfdb_id)
        make_parent(unpublished_dataset, 4)

        response = client.get(reverse("ghfdb-parent-table"))

        assert response.context["result_count"] == 3

    def test_a_contributor_sees_the_parents_of_their_private_dataset_too(
        self, client, published_dataset, unpublished_dataset, member
    ):
        make_parent(published_dataset, 1)
        make_parent(unpublished_dataset, 2)
        client.force_login(member)

        response = client.get(reverse("ghfdb-parent-table"))

        assert listed_parents(response) == [1, 2]

    def test_one_more_parent_than_a_page_holds_makes_a_second_page_of_one(
        self, client, published_dataset
    ):
        for ghfdb_id in range(1, GHFDBParentTableView.paginate_by + 2):
            make_parent(published_dataset, ghfdb_id)

        first = client.get(reverse("ghfdb-parent-table"))
        second = client.get(reverse("ghfdb-parent-table"), {"page": 2})

        assert len(listed_parents(first)) == GHFDBParentTableView.paginate_by
        assert listed_parents(second) == [GHFDBParentTableView.paginate_by + 1]

    def test_the_query_count_is_the_same_for_three_parents_and_for_thirty(
        self, client, published_dataset, constant_query_count
    ):
        counter = iter(range(1, 1000))

        def build(count):
            for _ in range(count):
                make_parent(published_dataset, next(counter))

        def call():
            client.get(reverse("ghfdb-parent-table"))

        constant_query_count(build, call, low=3, high=27)
