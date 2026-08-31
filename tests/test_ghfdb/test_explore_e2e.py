"""The map viewer fills the shell on every device (issue #192).

A rendered-HTML test can only assert which classes are on which element. The
bug report is about *computed layout* on a phone, and only a browser can
settle that: at desktop widths the sidebar is a persistent column sharing the
grid row with ``.drawer-content``, so the content inherits a height for free.
Below the sidebar breakpoint the sidebar is an overlay drawer, out of flow,
contributing no height at all — so a fix proven only at desktop width proves
nothing about the reported bug.
"""

import pytest

from tests.conftest import requires_browser

pytestmark = [pytest.mark.e2e, requires_browser]


@pytest.fixture(autouse=True)
def _allow_async_db_teardown(monkeypatch):
    """Playwright's sync API leaves a running event loop on this thread, which
    trips Django's async-safety guard when ``live_server`` flushes the test
    database at teardown — nothing in the app runs on this thread, so the
    guard has nothing to protect here. See Django's own escape hatch for
    exactly this class of false positive."""
    monkeypatch.setenv("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


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


class TestExploreMapFillsTheShell:
    """The map viewer, at the viewport the bug was reported at."""

    @at_every_viewport
    def test_the_map_never_computes_to_zero_height(self, page, live_server, viewport):
        """The failure mode #192 reports: the map renders into nothing on a
        phone. iframe/Leaflet content measures its container once, so a
        container that computes to zero shows nothing, with no error."""
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
