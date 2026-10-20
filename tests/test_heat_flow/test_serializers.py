import pytest
from django.core.checks import run_checks
from fairdm.contrib.contributors.choices import ContributionLevel
from fairdm.factories import UserFactory
from heat_flow.models import HeatFlowSite
from research_vocabs.models import Concept

from tests.factories import (
    HeatFlowFactory,
    HeatFlowIntervalFactory,
    HeatFlowSiteFactory,
    ParentHeatFlowFactory,
)

SITES = "/api/v1/samples/heat-flow-sites/"
INTERVALS = "/api/v1/samples/depth-intervals/"
CHILDREN = "/api/v1/measurements/heat-flow/"
GRADIENTS = "/api/v1/measurements/thermal-gradients/"
CONDUCTIVITIES = "/api/v1/measurements/thermal-conductivities/"
PARENTS = "/api/v1/measurements/parent-heat-flow/"

ROUTES = {
    "site": SITES,
    "interval": INTERVALS,
    "child": CHILDREN,
    "gradient": GRADIENTS,
    "conductivity": CONDUCTIVITIES,
    "parent": PARENTS,
}

# Written from the model declarations, so a quantity field that goes missing from
# `units`, or one that appears without being declared, fails.
UNITS = {
    "site": {
        "azimuth": "deg",
        "inclination": "deg",
        "length": "m",
        "elevation": "m",
    },
    "interval": {"top": "m", "bottom": "m", "vertical_depth": "m"},
    "child": {"value": "mW/m²", "uncertainty": "mW/m²"},
    "gradient": {
        "value": "K/km",
        "uncertainty": "K/km",
        "corrected_value": "K/km",
        "corrected_uncertainty": "K/km",
        "shutin_top": "h",
        "shutin_bottom": "h",
    },
    "conductivity": {"value": "W/mK", "uncertainty": "W/mK"},
    "parent": {"value": "mW/m²", "uncertainty": "mW/m²"},
}


def only_record(client, route):
    response = client.get(route)

    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) == 1
    return results[0]


def expected_term(concept):
    return {
        "name": concept.name,
        "label": concept.label,
        "uri": concept.uri,
        "vocabulary": concept.vocabulary.name,
    }


def stored_term(vocabulary_name, name):
    return expected_term(
        Concept.objects.get(vocabulary__name=vocabulary_name, name=name)
    )


@pytest.mark.django_db
class TestHeatFlowRecordSerializer:
    @pytest.mark.parametrize("kind", ROUTES)
    def test_every_list_answers_200_with_its_record(self, client, full_records, kind):
        response = client.get(ROUTES[kind])

        assert response.status_code == 200
        assert response.json()["count"] == 1

    def test_a_single_term_carries_name_label_uri_and_vocabulary(
        self, client, full_records
    ):
        record = only_record(client, SITES)

        vocabulary = HeatFlowSite._meta.get_field("environment").scheme.scheme().name
        assert record["environment"] == stored_term(vocabulary, "onshore_continental")

    def test_an_empty_single_term_is_null(self, client, full_records):
        HeatFlowSite.objects.update(explo_method=None)

        record = only_record(client, SITES)

        assert record["explo_method"] is None

    def test_a_many_valued_term_gives_one_entry_per_term(self, client, full_records):
        gradient = full_records["gradient"]
        top = list(gradient.method_top.order_by("name"))

        record = only_record(client, GRADIENTS)

        assert len(top) >= 1
        assert sorted(record["method_top"], key=lambda term: term["name"]) == [
            expected_term(concept) for concept in top
        ]

    def test_a_site_with_two_terms_for_a_field_lists_both(self, client, full_records):
        purposes = list(full_records["site"].explo_purpose.order_by("name"))

        record = only_record(client, SITES)

        assert len(purposes) == 2
        assert sorted(record["explo_purpose"], key=lambda term: term["name"]) == [
            expected_term(concept) for concept in purposes
        ]

    def test_a_many_valued_term_with_nothing_chosen_is_an_empty_list(
        self, client, full_records
    ):
        full_records["site"].age.clear()

        record = only_record(client, SITES)

        assert record["age"] == []

    def test_a_quantity_is_the_stored_magnitude_in_its_declared_unit(
        self, client, full_records
    ):
        record = only_record(client, SITES)

        assert record["azimuth"] == 45.5
        assert record["inclination"] == 10.25
        # Entered in feet, stored and given in metres.
        assert record["length"] == pytest.approx(304.8)

    def test_a_site_carries_its_elevation_with_its_datum_and_type(
        self, client, full_records
    ):
        record = only_record(client, SITES)

        assert record["elevation"] == 250
        assert record["elevation_datum"]["name"] == "MSL"
        assert record["type"]["name"] == "unknown"

    @pytest.mark.parametrize(
        ("kind", "name", "expected"),
        [
            ("child", "value", 70.5),
            ("parent", "uncertainty", 4.5),
            ("interval", "top", 10.5),
            ("interval", "vertical_depth", 190),
        ],
    )
    def test_a_float_quantity_is_a_json_number(
        self, client, full_records, kind, name, expected
    ):
        record = only_record(client, ROUTES[kind])

        assert record[name] == expected
        assert not isinstance(record[name], str)

    @pytest.mark.parametrize(
        ("kind", "name", "expected"),
        [
            ("gradient", "value", 25.5),
            ("gradient", "corrected_uncertainty", 1.5),
            ("conductivity", "value", 2.5),
            ("conductivity", "uncertainty", 0.25),
        ],
    )
    def test_a_decimal_quantity_is_a_json_number(
        self, client, full_records, kind, name, expected
    ):
        record = only_record(client, ROUTES[kind])

        assert record[name] == expected
        assert isinstance(record[name], float)

    def test_an_integer_quantity_is_a_json_integer(self, client, full_records):
        record = only_record(client, GRADIENTS)

        assert record["shutin_top"] == 12
        assert isinstance(record["shutin_top"], int)

    @pytest.mark.parametrize("kind", ROUTES)
    def test_units_names_every_quantity_with_its_declared_unit(
        self, client, full_records, kind
    ):
        record = only_record(client, ROUTES[kind])

        assert record["units"] == UNITS[kind]

    def test_an_empty_quantity_is_null_and_its_unit_is_still_given(
        self, client, full_records
    ):
        child = full_records["child"]
        type(child).objects.filter(pk=child.pk).update(uncertainty=None)

        record = only_record(client, CHILDREN)

        assert record["uncertainty"] is None
        assert record["units"]["uncertainty"] == "mW/m²"


@pytest.mark.django_db
class TestHeatFlowWrites:
    @pytest.fixture
    def writer(self, client, public_dataset):
        user = UserFactory()
        credit = public_dataset.add_contributor(user)
        credit.level = ContributionLevel.EDIT
        credit.save()
        client.force_login(user)
        return client

    def create_site(self, writer, dataset, **extra):
        # The many-valued fields are sent empty, as the generated serializer
        # requires them to be present and could not read anything else.
        body = {
            "name": "Written site",
            "dataset": dataset.uuid,
            "environment": "onshore_continental",
            "explo_purpose": [],
            "lithology": [],
            "age": [],
            "stratigraphy": [],
            **extra,
        }
        return writer.post(SITES, body, content_type="application/json")

    def test_a_site_is_created_with_a_terms_name_and_stores_that_term(
        self, writer, public_dataset
    ):
        response = self.create_site(writer, public_dataset)

        assert response.status_code == 201, response.content
        site = HeatFlowSite.objects.get(name="Written site")
        assert str(site.environment) == "onshore_continental"
        assert response.json()["environment"]["name"] == "onshore_continental"

    def test_a_quantity_written_as_a_number_is_stored_and_read_back(
        self, writer, public_dataset
    ):
        response = self.create_site(writer, public_dataset, azimuth=30.5)

        assert response.status_code == 201, response.content
        assert response.json()["azimuth"] == 30.5
        assert HeatFlowSite.objects.get(name="Written site").azimuth.magnitude == 30.5

    def test_a_write_supplying_stratigraphy_leaves_it_unchanged(
        self, writer, public_dataset
    ):
        response = self.create_site(writer, public_dataset, stratigraphy=["Jurassic"])

        assert response.status_code == 201, response.content
        site = HeatFlowSite.objects.get(name="Written site")
        assert site.stratigraphy.count() == 0

    def test_the_system_checks_report_no_unwritable_required_field(self, db):
        errors = [error for error in run_checks() if error.id == "fairdm.E600"]

        assert errors == []


def detail(client, route, record):
    response = client.get(f"{route}{record.uuid}/")

    assert response.status_code == 200
    return response.json()


def uuids(entries):
    return {entry["uuid"] for entry in entries}


@pytest.mark.django_db
class TestHeatFlowSiteSerializer:
    def test_the_single_site_carries_its_parent_whole(self, client, site_graph):
        parent = site_graph["parent"]

        record = detail(client, SITES, site_graph["site"])

        assert record["parent"]["uuid"] == parent.uuid
        assert record["parent"]["value"] == 65.5
        assert record["parent"]["uncertainty"] == 4.5
        assert record["parent"]["quality"] == parent.quality
        assert record["parent"]["ghfdb_id"] == parent.ghfdb_id

    def test_the_single_site_carries_every_interval_with_its_children(
        self, client, site_graph
    ):
        record = detail(client, SITES, site_graph["site"])

        assert uuids(record["intervals"]) == {
            interval.uuid for interval in site_graph["intervals"]
        }
        for entry, interval in zip(
            sorted(record["intervals"], key=lambda entry: entry["top"]),
            site_graph["intervals"],
            strict=True,
        ):
            assert uuids(entry["children"]) == {
                child.uuid for child in site_graph["children"][interval.pk]
            }

    def test_an_interval_with_two_children_lists_both_whole(self, client, site_graph):
        record = detail(client, SITES, site_graph["site"])

        shallow = min(record["intervals"], key=lambda entry: entry["top"])
        assert {child["uuid"]: child["value"] for child in shallow["children"]} == {
            child.uuid: child.value for child in site_graph["all_children"][:2]
        }

    def test_the_site_list_carries_position_and_the_parents_headline(
        self, client, site_graph
    ):
        parent = site_graph["parent"]

        record = only_record(client, SITES)

        assert record["location"]["type"] == "Point"
        assert record["parent"] == {
            "uuid": parent.uuid,
            "url": record["parent"]["url"],
            "value": 65.5,
            "uncertainty": 4.5,
            "quality": parent.quality,
            "units": {"value": "mW/m²", "uncertainty": "mW/m²"},
        }
        assert record["parent"]["url"].endswith(f"{PARENTS}{parent.uuid}/")
        assert "intervals" not in record

    def test_a_site_with_no_parent_is_listed_with_a_null_parent(
        self, client, public_dataset
    ):
        site = HeatFlowSiteFactory(dataset=public_dataset)

        listed = only_record(client, SITES)
        single = detail(client, SITES, site)

        assert listed["parent"] is None
        assert single["parent"] is None
        assert single["intervals"] == []

    def test_a_hidden_parent_is_null_on_the_site_in_both_shapes(
        self, client, site_graph, private_dataset
    ):
        type(site_graph["parent"]).objects.filter(pk=site_graph["parent"].pk).update(
            dataset=private_dataset
        )

        listed = only_record(client, SITES)
        single = detail(client, SITES, site_graph["site"])

        assert listed["parent"] is None
        assert single["parent"] is None

    def test_a_hidden_interval_and_a_hidden_child_are_absent_from_the_site(
        self, client, site_graph, private_dataset
    ):
        deep = site_graph["intervals"][1]
        hidden_child = site_graph["children"][site_graph["intervals"][0].pk][1]
        type(deep).objects.filter(pk=deep.pk).update(dataset=private_dataset)
        type(hidden_child).objects.filter(pk=hidden_child.pk).update(
            dataset=private_dataset
        )

        record = detail(client, SITES, site_graph["site"])

        assert uuids(record["intervals"]) == {site_graph["intervals"][0].uuid}
        assert uuids(record["intervals"][0]["children"]) == {
            site_graph["children"][site_graph["intervals"][0].pk][0].uuid
        }

    def test_the_site_list_costs_the_same_for_one_site_as_for_several(
        self, client, public_dataset, constant_query_count
    ):
        def build(count):
            for _ in range(count):
                site = HeatFlowSiteFactory(dataset=public_dataset)
                ParentHeatFlowFactory(dataset=public_dataset, sample=site)

        constant_query_count(build, lambda: client.get(SITES, {"page_size": 100}))

    def test_a_single_site_costs_the_same_with_more_intervals_and_children(
        self, client, public_dataset, constant_query_count
    ):
        site = HeatFlowSiteFactory(dataset=public_dataset)
        parent = ParentHeatFlowFactory(dataset=public_dataset, sample=site)

        def build(count):
            for _ in range(count):
                interval = HeatFlowIntervalFactory(dataset=public_dataset, site=site)
                for _ in range(2):
                    HeatFlowFactory(
                        dataset=public_dataset, sample=interval, parent=parent
                    )

        constant_query_count(
            build, lambda: client.get(f"{SITES}{site.uuid}/"), low=1, high=3
        )


@pytest.mark.django_db
class TestParentHeatFlowSerializer:
    def test_the_single_parent_carries_its_values_scores_site_and_children(
        self, client, site_graph
    ):
        parent = site_graph["parent"]

        record = detail(client, PARENTS, parent)

        assert record["value"] == 65.5
        assert record["uncertainty"] == 4.5
        assert record["U_score"] == parent.U_score
        assert record["M_score"] == parent.M_score
        assert record["quality"] == parent.quality
        assert record["quality_scheme"] == parent.quality_scheme
        assert record["ghfdb_id"] == parent.ghfdb_id
        assert record["site"]["uuid"] == site_graph["site"].uuid

    def test_every_child_is_listed_with_whether_it_is_relevant(
        self, client, site_graph
    ):
        record = detail(client, PARENTS, site_graph["parent"])

        assert {
            child["uuid"]: child["is_relevant"] for child in record["children"]
        } == {child.uuid: child.is_relevant for child in site_graph["all_children"]}
        assert False in {child["is_relevant"] for child in record["children"]}
        assert all(child["url"] for child in record["children"])

    def test_a_hidden_child_is_absent_from_the_parents_children(
        self, client, site_graph, private_dataset
    ):
        hidden = site_graph["all_children"][0]
        type(hidden).objects.filter(pk=hidden.pk).update(dataset=private_dataset)

        record = detail(client, PARENTS, site_graph["parent"])

        assert uuids(record["children"]) == {
            child.uuid for child in site_graph["all_children"][1:]
        }

    def test_the_parent_list_carries_the_site_and_scores_but_no_children(
        self, client, site_graph
    ):
        record = only_record(client, PARENTS)

        assert record["site"]["uuid"] == site_graph["site"].uuid
        assert record["quality"] == site_graph["parent"].quality
        assert "children" not in record

    def test_the_parent_list_costs_the_same_for_one_parent_as_for_several(
        self, client, public_dataset, constant_query_count
    ):
        def build(count):
            for _ in range(count):
                site = HeatFlowSiteFactory(dataset=public_dataset)
                ParentHeatFlowFactory(dataset=public_dataset, sample=site)

        constant_query_count(build, lambda: client.get(PARENTS, {"page_size": 100}))

    def test_a_single_parent_costs_the_same_with_more_children(
        self, client, public_dataset, constant_query_count
    ):
        parent = ParentHeatFlowFactory(dataset=public_dataset)
        interval = HeatFlowIntervalFactory(dataset=public_dataset, site=parent.sample)

        def build(count):
            for _ in range(count):
                HeatFlowFactory(dataset=public_dataset, sample=interval, parent=parent)

        constant_query_count(build, lambda: client.get(f"{PARENTS}{parent.uuid}/"))
