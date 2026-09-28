import pytest
from django.urls import reverse

from tests.conftest import requires_browser


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
