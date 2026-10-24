import pytest
from bs4 import BeautifulSoup
from django.urls import reverse

EXPLORE = reverse("ghfdb-explore")
PARENT_TABLE = reverse("ghfdb-parent-table")


def sidebar_links(client, url):
    """Render *url* and return its parsed page."""
    response = client.get(url)
    assert response.status_code == 200
    return BeautifulSoup(response.content, "html.parser")


def link_to(soup, href):
    """The first sidebar link pointing at *href*, or None."""
    return soup.select_one(f'.menu a[href="{href}"]')


@pytest.mark.django_db
class TestGHFDBMenuGroup:
    def test_both_entries_sit_inside_one_collapsible_group(self, client):
        soup = sidebar_links(client, EXPLORE)

        map_viewer = link_to(soup, EXPLORE)
        parent_table = link_to(soup, PARENT_TABLE)

        group = map_viewer.find_parent("details")
        assert group is not None
        assert parent_table.find_parent("details") is group

    def test_the_map_viewer_comes_before_the_parent_table(self, client):
        soup = sidebar_links(client, EXPLORE)

        group = link_to(soup, EXPLORE).find_parent("details")
        hrefs = [a["href"] for a in group.select("ul a[href]")]

        assert hrefs == [EXPLORE, PARENT_TABLE]

    def test_the_group_sits_where_the_map_viewer_entry_was(self, client):
        soup = sidebar_links(client, EXPLORE)

        entry = link_to(soup, EXPLORE).find_parent("details").find_parent("li")
        following = entry.find_next_sibling("li")

        assert following.select_one(f'a[href="{reverse("project-list")}"]')

    @pytest.mark.parametrize("url", [EXPLORE, PARENT_TABLE])
    def test_the_group_is_open_on_either_page(self, client, url):
        soup = sidebar_links(client, url)

        assert link_to(soup, url).find_parent("details").has_attr("open")

    @pytest.mark.parametrize(
        ("url", "other"), [(EXPLORE, PARENT_TABLE), (PARENT_TABLE, EXPLORE)]
    )
    def test_only_the_current_entry_is_marked_current(self, client, url, other):
        soup = sidebar_links(client, url)

        assert link_to(soup, url).get("aria-current") == "page"
        assert link_to(soup, other).get("aria-current") is None

    def test_the_group_is_closed_on_a_page_it_does_not_hold(self, client):
        soup = sidebar_links(client, reverse("project-list"))

        assert not link_to(soup, EXPLORE).find_parent("details").has_attr("open")
