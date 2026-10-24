import re

import pytest
from bs4 import BeautifulSoup
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from project.ghfdb.views import GHFDBParentTableView
from tests.conftest import requires_browser

from .conftest import build_child, make_parent


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


def children_button(response, ghfdb_id):
    """The count button in the row of one parent."""
    page = BeautifulSoup(response.content, "html.parser")
    row = page.select_one(f'tr[data-ghfdb="parent-row"][data-parent="{ghfdb_id}"]')
    return row.select_one('[data-ghfdb="children-count"]')


@pytest.mark.django_db
class TestGHFDBParentTableChildCounts:
    def test_the_button_carries_the_number_of_children_and_of_relevant_ones(
        self, client, published_dataset
    ):
        parent = make_parent(published_dataset, 1)
        build_child(published_dataset, parent, ghfdb_id=11, is_relevant=True)
        build_child(published_dataset, parent, ghfdb_id=12, is_relevant=True)
        build_child(published_dataset, parent, ghfdb_id=13)

        button = children_button(client.get(reverse("ghfdb-parent-table")), 1)

        assert (button["data-total"], button["data-relevant"]) == ("3", "2")

    def test_a_parent_none_of_whose_children_is_relevant_counts_zero_relevant(
        self, client, published_dataset
    ):
        parent = make_parent(published_dataset, 1)
        build_child(published_dataset, parent, ghfdb_id=11)

        button = children_button(client.get(reverse("ghfdb-parent-table")), 1)

        assert (button["data-total"], button["data-relevant"]) == ("1", "0")

    def test_the_button_loads_the_parents_children_from_their_address(
        self, client, published_dataset
    ):
        make_parent(published_dataset, 4)

        button = children_button(client.get(reverse("ghfdb-parent-table")), 4)

        assert button["hx-get"] == reverse("ghfdb-parent-children", args=[4])

    def test_a_relevant_child_in_an_unpublished_dataset_is_counted_by_nobody_outside_it(
        self, client, published_dataset, unpublished_dataset
    ):
        parent = make_parent(published_dataset, 1)
        build_child(published_dataset, parent, ghfdb_id=11)
        build_child(unpublished_dataset, parent, ghfdb_id=12, is_relevant=True)

        button = children_button(client.get(reverse("ghfdb-parent-table")), 1)

        assert (button["data-total"], button["data-relevant"]) == ("1", "0")

    def test_a_contributor_on_that_dataset_has_it_counted_in_both_numbers(
        self, client, published_dataset, unpublished_dataset, member
    ):
        parent = make_parent(published_dataset, 1)
        build_child(published_dataset, parent, ghfdb_id=11)
        build_child(unpublished_dataset, parent, ghfdb_id=12, is_relevant=True)
        client.force_login(member)

        button = children_button(client.get(reverse("ghfdb-parent-table")), 1)

        assert (button["data-total"], button["data-relevant"]) == ("2", "1")


@pytest.mark.django_db
class TestGHFDBParentTableFilters:
    @pytest.fixture
    def parents(self, published_dataset):
        make_parent(
            published_dataset,
            1,
            value=20,
            U_score="U1",
            site={"environment": "onshore_continental"},
        )
        make_parent(
            published_dataset,
            2,
            value=60,
            U_score="U1",
            site={"environment": "onshore_continental"},
        )
        make_parent(
            published_dataset,
            3,
            value=60,
            U_score="U2",
            site={"environment": "onshore_marine"},
        )

    def test_several_filters_together_list_only_parents_matching_all_with_the_count(
        self, client, parents
    ):
        response = client.get(
            reverse("ghfdb-parent-table"),
            {"q_min": "50", "U_score": ["U1"], "environment": ["onshore_continental"]},
        )

        assert listed_parents(response) == [2]
        assert response.context["result_count"] == 1

    def test_the_same_address_in_a_fresh_client_gives_the_same_rows_in_the_same_order(
        self, client, parents
    ):
        address = reverse("ghfdb-parent-table")
        query = {"q_min": "10", "sort": "-q"}

        first = client.get(address, query)
        second = Client().get(address, query)

        assert listed_parents(first) == listed_parents(second)
        assert listed_parents(first) == [2, 3, 1]

    def test_filters_that_match_nothing_leave_no_rows_and_a_link_to_clear_them(
        self, client, parents
    ):
        response = client.get(reverse("ghfdb-parent-table"), {"q_min": "1000"})

        assert listed_parents(response) == []
        assert response.context["result_count"] == 0
        clear = response.context["clear_refinements_url"]
        assert f'href="{clear}"' in response.content.decode()

    def test_a_bound_that_is_not_a_number_or_is_inverted_is_reported_and_narrows_nothing(
        self, client, parents
    ):
        address = reverse("ghfdb-parent-table")

        not_a_number = client.get(address, {"q_min": "abc"})
        inverted = client.get(address, {"q_min": "100", "q_max": "10"})

        for response, code in ((not_a_number, "invalid"), (inverted, "inverted")):
            errors = response.context["filter"].form.errors.as_data()
            assert [error.code for error in errors["q"]] == [code]
            assert listed_parents(response) == [1, 2, 3]

    def test_the_toolbar_holds_the_search_and_the_three_checkbox_filters(
        self, client, parents
    ):
        response = client.get(reverse("ghfdb-parent-table"))

        toolbar = [field["name"] for field in response.context["toolbar_fields"]]
        panel = [field.name for field in response.context["panel_fields"]]
        assert toolbar == ["name", "corr_HP_flag", "U_score", "M_score"]
        assert set(panel) == set(response.context["filter"].filters) - set(toolbar)
        assert panel.index("project") < panel.index("dataset")


def window(response):
    """The children listed in a fragment, in order, as ``(pk, relevant, badged)``."""
    page = BeautifulSoup(response.content, "html.parser")
    return [
        (
            int(row["data-child"]),
            row["data-relevant"] == "true",
            row.select_one('[data-ghfdb="relevant-badge"]') is not None,
        )
        for row in page.select('[data-heat-flow="child"]')
    ]


def select_list(sql):
    """The outermost select list of a query, without anything in parentheses."""
    flat = sql
    while True:
        stripped = re.sub(r"\([^()]*\)", "", flat)
        if stripped == flat:
            break
        flat = stripped
    return flat.split(" FROM ")[0]


@pytest.mark.django_db
class TestGHFDBParentChildrenView:
    @pytest.fixture
    def parent(self, published_dataset):
        return make_parent(published_dataset, 1)

    def address(self, ghfdb_id=1):
        return reverse("ghfdb-parent-children", args=[ghfdb_id])

    def test_every_child_is_listed_the_relevant_ones_first_and_only_they_are_badged(
        self, client, published_dataset, parent
    ):
        plain = build_child(published_dataset, parent, ghfdb_id=11)
        relevant = build_child(published_dataset, parent, ghfdb_id=12, is_relevant=True)
        later = build_child(published_dataset, parent, ghfdb_id=13, is_relevant=True)

        listed = window(client.get(self.address()))

        assert listed == [
            (relevant.pk, True, True),
            (later.pk, True, True),
            (plain.pk, False, False),
        ]

    def test_each_child_links_to_its_page_and_shows_its_quality_code(
        self, client, published_dataset, parent
    ):
        child = build_child(published_dataset, parent, ghfdb_id=11)

        page = BeautifulSoup(client.get(self.address()).content, "html.parser")

        row = page.select_one(f'[data-heat-flow="child"][data-child="{child.pk}"]')
        assert row.select_one(f'a[href="{child.get_absolute_url()}"]') is not None
        assert row.select_one('[data-quality="code"]') is not None

    def test_a_child_in_an_unpublished_dataset_is_counted_but_not_named(
        self, client, published_dataset, unpublished_dataset, parent
    ):
        shown = build_child(published_dataset, parent, ghfdb_id=11)
        build_child(unpublished_dataset, parent, ghfdb_id=12, is_relevant=True)

        response = client.get(self.address())

        assert [pk for pk, _, _ in window(response)] == [shown.pk]
        assert response.context["children"]["hidden"] == 1

    def test_a_contributor_on_that_dataset_is_shown_the_child(
        self, client, published_dataset, unpublished_dataset, member, parent
    ):
        build_child(published_dataset, parent, ghfdb_id=11)
        hidden = build_child(unpublished_dataset, parent, ghfdb_id=12, is_relevant=True)
        client.force_login(member)

        response = client.get(self.address())

        assert hidden.pk in [pk for pk, _, _ in window(response)]
        assert response.context["children"]["hidden"] == 0

    def test_a_parent_the_visitor_may_not_see_answers_not_found(
        self, client, unpublished_dataset
    ):
        make_parent(unpublished_dataset, 2)

        assert client.get(self.address(2)).status_code == 404

    def test_an_unknown_parent_answers_not_found(self, client, db):
        assert client.get(self.address(999)).status_code == 404

    def test_the_query_count_is_the_same_for_two_children_and_for_ten(
        self, client, published_dataset, parent, constant_query_count
    ):
        counter = iter(range(100, 1000))

        def build(count):
            for _ in range(count):
                build_child(published_dataset, parent, ghfdb_id=next(counter))

        def call():
            client.get(self.address())

        constant_query_count(build, call, low=2, high=10)


@pytest.mark.django_db
class TestGHFDBParentTableLoadsNoChildren:
    def test_no_row_carries_children_and_no_query_selects_a_child_column(
        self, client, published_dataset
    ):
        parent = make_parent(published_dataset, 1)
        build_child(published_dataset, parent, ghfdb_id=11, is_relevant=True)

        with CaptureQueriesContext(connection) as queries:
            response = client.get(reverse("ghfdb-parent-table"))

        for row in response.context["table"].paginated_rows:
            assert "children" not in getattr(
                row.record, "_prefetched_objects_cache", {}
            )
        selected = [select_list(query["sql"]) for query in queries.captured_queries]
        assert not [sql for sql in selected if '"heat_flow_heatflow".' in sql]


@pytest.mark.django_db
class TestGHFDBParentCountsMatchTheirWindow:
    @pytest.mark.parametrize("signed_in", [False, True], ids=["visitor", "member"])
    def test_a_rows_count_is_the_children_listed_and_its_bracket_the_ones_badged(
        self,
        client,
        published_dataset,
        unpublished_dataset,
        member,
        signed_in,
    ):
        parent = make_parent(published_dataset, 1)
        build_child(published_dataset, parent, ghfdb_id=11, is_relevant=True)
        build_child(published_dataset, parent, ghfdb_id=12)
        build_child(unpublished_dataset, parent, ghfdb_id=13, is_relevant=True)
        if signed_in:
            client.force_login(member)

        button = children_button(client.get(reverse("ghfdb-parent-table")), 1)
        listed = window(client.get(button["hx-get"]))

        assert int(button["data-total"]) == len(listed)
        assert int(button["data-relevant"]) == len([row for row in listed if row[2]])


@pytest.mark.e2e
@requires_browser
class TestGHFDBParentChildrenDialog:
    def test_pressing_a_count_opens_that_parents_children_and_closing_leaves_the_address(
        self, page, live_server, published_dataset
    ):
        first = make_parent(published_dataset, 1)
        second = make_parent(published_dataset, 2)
        build_child(published_dataset, first, ghfdb_id=11, is_relevant=True)
        shown = build_child(published_dataset, second, ghfdb_id=21)
        other = build_child(published_dataset, second, ghfdb_id=22, is_relevant=True)
        address = f"{live_server.url}{reverse('ghfdb-parent-table')}"
        page.goto(address)

        page.click('[data-parent="2"] [data-ghfdb="children-count"]')

        dialog = page.locator("#children-dialog")
        dialog.wait_for(state="visible")
        listed = dialog.locator('[data-heat-flow="child"]')
        assert sorted(
            int(pk)
            for pk in listed.evaluate_all("rows => rows.map(r => r.dataset.child)")
        ) == sorted([shown.pk, other.pk])
        dialog.locator("form[method=dialog] button[aria-label]").click()
        dialog.wait_for(state="hidden")
        assert page.url == address
