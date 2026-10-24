import pytest
from django.contrib.gis.geos import Point
from heat_flow import vocabularies
from heat_flow.models import ParentHeatFlow
from research_vocabs.models import Concept

from project.ghfdb.tables import GHFDBParentTable

from .conftest import build_child, make_parent, parents, purposes

NOT_RECORDED = 'data-state="not-recorded"'


def rows_by_id(table):
    return {row.record.ghfdb_id: row for row in table.rows}


def order_of(order_by):
    return [
        row.record.ghfdb_id
        for row in GHFDBParentTable(parents(), order_by=order_by).rows
    ]


@pytest.mark.django_db
class TestGHFDBParentTable:
    def test_a_parent_renders_each_published_value_in_its_column(
        self, published_dataset
    ):
        make_parent(
            published_dataset,
            7,
            purpose=["hydrocarbon"],
            site={
                "name": "Borehole Alpha",
                "location": Point(11.5678, 48.1234, srid=4326),
                "elevation": 321,
                "length": 1500,
                "vertical_depth": 1450,
            },
            value=63.5,
            uncertainty=4.5,
            comment="a remark",
        )

        row = rows_by_id(GHFDBParentTable(parents()))[7]

        assert "63.5" in row.get_cell("q")
        assert "4.5" in row.get_cell("q_uncertainty")
        assert "48.1234" in row.get_cell("lat_NS")
        assert "11.5678" in row.get_cell("long_EW")
        assert "321" in row.get_cell("elevation")
        assert "1500" in row.get_cell("total_depth_MD")
        assert "1450" in row.get_cell("total_depth_TVD")
        assert "Borehole Alpha" in row.get_cell("name")
        assert "a remark" in row.get_cell("p_comment")

    def test_a_vocabulary_column_renders_the_terms_label_not_its_stored_key(
        self, published_dataset
    ):
        make_parent(
            published_dataset,
            1,
            site={"environment": "offshore_marine", "explo_method": "probing_offshore"},
        )
        environment = Concept.objects.get(
            vocabulary__name=vocabularies.GeographicEnvironment().scheme().name,
            name="offshore_marine",
        )
        method = Concept.objects.get(
            vocabulary__name=vocabularies.ExplorationMethod().scheme().name,
            name="probing_offshore",
        )

        row = rows_by_id(GHFDBParentTable(parents()))[1]

        assert str(environment.label) in row.get_cell("environment")
        assert "offshore_marine" not in row.get_cell("environment")
        assert str(method.label) in row.get_cell("explo_method")
        assert "probing_offshore" not in row.get_cell("explo_method")

    @pytest.mark.parametrize(
        "column",
        [
            "q_uncertainty",
            "elevation",
            "total_depth_MD",
            "total_depth_TVD",
            "corr_HP_flag",
            "p_comment",
            "explo_purpose",
        ],
    )
    def test_a_missing_value_renders_as_not_recorded(self, published_dataset, column):
        make_parent(
            published_dataset,
            1,
            site={"elevation": None, "length": None, "vertical_depth": None},
            uncertainty=None,
            corr_HP_flag=None,
            comment="",
        )

        row = rows_by_id(GHFDBParentTable(parents()))[1]

        assert NOT_RECORDED in row.get_cell(column)

    @pytest.mark.parametrize(
        "column", ["q_uncertainty", "elevation", "total_depth_MD", "total_depth_TVD"]
    )
    def test_a_value_of_zero_renders_as_zero_not_as_not_recorded(
        self, published_dataset, column
    ):
        make_parent(
            published_dataset,
            1,
            site={"elevation": 0, "length": 0, "vertical_depth": 0},
            uncertainty=0,
        )

        cell = rows_by_id(GHFDBParentTable(parents()))[1].get_cell(column)

        assert NOT_RECORDED not in cell
        assert "0" in cell

    def test_a_parent_without_children_renders_a_count_of_zero(self, published_dataset):
        make_parent(published_dataset, 1)

        cell = rows_by_id(GHFDBParentTable(parents()))[1].get_cell("children")

        assert NOT_RECORDED not in cell
        assert "0" in cell

    def test_a_false_flag_renders_as_recorded(self, published_dataset):
        make_parent(published_dataset, 1, corr_HP_flag=False)

        cell = rows_by_id(GHFDBParentTable(parents()))[1].get_cell("corr_HP_flag")

        assert NOT_RECORDED not in cell

    def test_the_identifier_links_to_the_parent_and_the_name_to_its_site(
        self, published_dataset
    ):
        parent = make_parent(published_dataset, 1)

        row = rows_by_id(GHFDBParentTable(parents()))[1]

        assert f'href="{parent.get_absolute_url()}"' in row.get_cell("ID_parent")
        assert f'href="{parent.sample.get_absolute_url()}"' in row.get_cell("name")

    def test_the_children_count_links_to_the_parents_children(self, published_dataset):
        from django.urls import reverse

        parent = make_parent(published_dataset, 4)
        build_child(published_dataset, parent, ghfdb_id=41, is_relevant=True)

        cell = rows_by_id(GHFDBParentTable(parents()))[4].get_cell("children")

        assert reverse("ghfdb-parent-children", args=[4]) in cell

    def test_several_exploration_purposes_are_joined_in_one_cell(
        self, published_dataset
    ):
        make_parent(published_dataset, 1, purpose=["hydrocarbon", "mining"])
        labels = [str(concept.label) for concept in purposes("hydrocarbon", "mining")]

        cell = rows_by_id(GHFDBParentTable(parents()))[1].get_cell("explo_purpose")

        assert all(label in cell for label in labels)


@pytest.mark.django_db
class TestGHFDBParentTableOrdering:
    @pytest.fixture
    def three(self, published_dataset):
        """Three parents that differ in every column, in an order matching no column."""
        rows = {
            1: {
                "value": 30,
                "uncertainty": 3,
                "comment": "b",
                "corr_HP_flag": None,
                "quality": "Q2",
                "purpose": ["mining"],
                "site": {
                    "name": "Beta",
                    "location": Point(20, 20, srid=4326),
                    "elevation": 20,
                    "length": 200,
                    "vertical_depth": 200,
                    "environment": "onshore_marine",
                    "explo_method": "mining",
                },
            },
            2: {
                "value": 10,
                "uncertainty": 1,
                "comment": "c",
                "corr_HP_flag": True,
                "quality": "Q3",
                "purpose": ["hydrocarbon", "research"],
                "site": {
                    "name": "Gamma",
                    "location": Point(30, 30, srid=4326),
                    "elevation": 30,
                    "length": 300,
                    "vertical_depth": 300,
                    "environment": "offshore_marine",
                    "explo_method": "tunneling",
                },
            },
            3: {
                "value": 20,
                "uncertainty": 2,
                "comment": "a",
                "corr_HP_flag": False,
                "quality": "Q1",
                "purpose": ["geothermal"],
                "site": {
                    "name": "Alpha",
                    "location": Point(10, 10, srid=4326),
                    "elevation": 10,
                    "length": 100,
                    "vertical_depth": 100,
                    "environment": "onshore_continental",
                    "explo_method": "drilling",
                },
            },
        }
        for ghfdb_id, fields in rows.items():
            quality = fields.pop("quality")
            parent = make_parent(published_dataset, ghfdb_id, **fields)
            ParentHeatFlow.objects.filter(pk=parent.pk).update(quality=quality)
        # children: parent 3 has none, parent 1 one, parent 2 two
        build_child(
            published_dataset, ParentHeatFlow.objects.get(ghfdb_id=1), ghfdb_id=11
        )
        for index in (21, 22):
            build_child(
                published_dataset,
                ParentHeatFlow.objects.get(ghfdb_id=2),
                ghfdb_id=index,
            )

    @pytest.mark.parametrize("column", list(GHFDBParentTable.base_columns))
    def test_every_column_sorts_in_both_directions(self, three, column):
        ascending = order_of(column)
        descending = order_of(f"-{column}")

        assert sorted(ascending) == [1, 2, 3]
        assert descending == ascending[::-1]

    def test_a_numeric_column_sorts_by_value(self, three):
        assert order_of("q") == [2, 3, 1]

    def test_the_children_column_sorts_by_how_many_there_are(self, three):
        assert order_of("children") == [3, 1, 2]

    def test_the_name_column_sorts_by_the_sites_name(self, three):
        assert order_of("name") == [3, 1, 2]

    def test_exploration_purpose_sorts_by_its_first_term_alphabetically(self, three):
        # geothermal (3), hydrocarbon (2, ahead of its second term), mining (1)
        assert order_of("explo_purpose") == [3, 2, 1]

    def test_the_comment_column_sorts_by_the_comment(self, three):
        assert order_of("p_comment") == [3, 1, 2]

    def test_a_sort_on_a_column_where_every_row_ties_lists_each_parent_once_across_pages(
        self, published_dataset
    ):
        for ghfdb_id in range(1, 6):
            make_parent(published_dataset, ghfdb_id, value=50, comment="same")

        for column in ("q", "children", "explo_purpose", "p_comment"):
            seen = []
            for page in (1, 2, 3):
                table = GHFDBParentTable(parents(), order_by=column)
                table.paginate(page=page, per_page=2)
                seen += [row.record.ghfdb_id for row in table.page.object_list]

            assert sorted(seen) == [1, 2, 3, 4, 5], column

    @pytest.mark.parametrize("order_by", [None, *GHFDBParentTable.base_columns])
    def test_every_ordering_ends_in_the_published_identifier_then_the_key(
        self, published_dataset, order_by
    ):
        # Postgres hands back tied rows in an order it may change between two
        # queries, so the tie-break is read off the query rather than guessed
        # from the rows of a small table. ghfdb_id is not unique in the schema,
        # so the primary key follows it.
        table = GHFDBParentTable(parents(), order_by=order_by)

        assert table.data.data.query.order_by[-2:] == ("ghfdb_id", "pk")

    def test_the_default_order_is_the_published_identifier(self, three):
        assert [row.record.ghfdb_id for row in GHFDBParentTable(parents()).rows] == [
            1,
            2,
            3,
        ]
