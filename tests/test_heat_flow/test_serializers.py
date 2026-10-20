import pytest
from django.core.checks import run_checks
from fairdm.contrib.contributors.choices import ContributionLevel
from fairdm.factories import UserFactory
from heat_flow.models import (
    HeatFlow,
    HeatFlowCorrection,
    HeatFlowSite,
    IntervalConductivity,
    ThermalGradient,
)
from research_vocabs.models import Concept

from tests.factories import (
    HeatFlowCorrectionFactory,
    HeatFlowFactory,
    HeatFlowIntervalFactory,
    HeatFlowSiteFactory,
    IntervalConductivityFactory,
    ParentHeatFlowFactory,
    ProbeMetadataFactory,
    ThermalGradientFactory,
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
    "child": {"value": "mW/m²", "uncertainty": "mW/m²", "surface_temperature": "°C"},
    "gradient": {
        "value": "K/km",
        "uncertainty": "K/km",
        "corrected_value": "K/km",
        "corrected_uncertainty": "K/km",
        "shutin_top": "h",
        "shutin_bottom": "h",
        "temperature_top": "°C",
        "temperature_top_uncertainty": "°C",
        "temperature_bottom": "°C",
        "temperature_bottom_uncertainty": "°C",
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


SCORES = (
    "U_score",
    "M_score",
    "T_score",
    "T_score_missing",
    "TC_score",
    "TC_score_missing",
    "quality",
    "quality_scheme",
)

CORRECTION_TYPES = HeatFlowCorrection.CorrectionTypeChoices
CORRECTION_STATUSES = HeatFlowCorrection.StatusChoices


def hide(record, dataset):
    type(record).objects.filter(pk=record.pk).update(dataset=dataset)


@pytest.mark.django_db
class TestHeatFlowSummarySerializer:
    def test_a_scored_child_carries_each_stored_score(self, client, full_records):
        child = full_records["child"]
        child.refresh_from_db()

        record = only_record(client, CHILDREN)

        assert child.quality_scheme
        assert {name: record[name] for name in SCORES} == {
            name: getattr(child, name) for name in SCORES
        }

    def test_an_unscored_child_has_null_numeric_scores(self, client, full_records):
        child = full_records["child"]
        type(child).objects.filter(pk=child.pk).update(T_score=None, TC_score=None)

        record = only_record(client, CHILDREN)

        assert record["T_score"] is None
        assert record["TC_score"] is None

    def test_the_child_carries_its_ghfdb_id_and_relevance(self, client, full_records):
        child = full_records["child"]
        type(child).objects.filter(pk=child.pk).update(ghfdb_id=4321, is_relevant=True)

        record = only_record(client, CHILDREN)

        assert record["ghfdb_id"] == 4321
        assert record["is_relevant"] is True

    def test_the_child_carries_its_surface_temperature_and_acquisition_date(
        self, client, full_records
    ):
        child = full_records["child"]
        type(child).objects.filter(pk=child.pk).update(
            surface_temperature=4.5, date_acquired="2019-06-12"
        )

        record = only_record(client, CHILDREN)

        assert record["surface_temperature"] == 4.5
        assert "surface_temperature" in record["units"]
        assert record["date_acquired"] == "2019-06-12"

    def test_a_child_with_no_surface_temperature_or_date_gives_null(
        self, client, full_records
    ):
        record = only_record(client, CHILDREN)

        assert record["surface_temperature"] is None
        assert record["date_acquired"] is None

    def test_the_child_carries_its_sites_coordinates(self, client, full_records):
        point = full_records["site"].location

        record = only_record(client, CHILDREN)

        assert record["location"]["type"] == "Point"
        assert record["location"]["coordinates"][:2] == [point.x, point.y]

    def test_the_child_refers_to_its_interval_parent_site_gradient_conductivity(
        self, client, full_records
    ):
        record = only_record(client, CHILDREN)

        assert record["sample"]["uuid"] == full_records["interval"].uuid
        assert record["parent"]["uuid"] == full_records["parent"].uuid
        assert record["site"]["uuid"] == full_records["site"].uuid
        assert record["thermal_gradient"]["uuid"] == full_records["gradient"].uuid
        assert (
            record["thermal_conductivity"]["uuid"] == full_records["conductivity"].uuid
        )
        assert record["site"]["url"].endswith(f"{SITES}{full_records['site'].uuid}/")

    def test_a_child_with_no_gradient_conductivity_or_parent_is_listed(
        self, client, public_dataset
    ):
        HeatFlowFactory(dataset=public_dataset)

        record = only_record(client, CHILDREN)

        assert record["parent"] is None
        assert record["thermal_gradient"] is None
        assert record["thermal_conductivity"] is None

    def test_a_negative_value_is_served_as_stored(self, client, full_records):
        child = full_records["child"]
        type(child).objects.filter(pk=child.pk).update(value=-12.5)

        record = only_record(client, CHILDREN)

        assert record["value"] == -12.5

    def test_a_child_whose_site_is_hidden_has_no_location_and_no_site(
        self, client, full_records, private_dataset
    ):
        hide(full_records["site"], private_dataset)

        record = only_record(client, CHILDREN)

        assert record["location"] is None
        assert record["site"] is None
        assert record["sample"]["uuid"] == full_records["interval"].uuid

    def test_a_hidden_gradient_is_a_null_reference_in_the_list(
        self, client, full_records, private_dataset
    ):
        hide(full_records["gradient"], private_dataset)

        record = only_record(client, CHILDREN)

        assert record["thermal_gradient"] is None
        assert record["thermal_conductivity"]["uuid"] == (
            full_records["conductivity"].uuid
        )

    def test_the_child_list_costs_the_same_for_one_child_as_for_several(
        self, client, public_dataset, constant_query_count
    ):
        def build(count):
            for _ in range(count):
                interval = HeatFlowIntervalFactory(dataset=public_dataset)
                HeatFlowFactory(
                    dataset=public_dataset,
                    sample=interval,
                    parent=ParentHeatFlowFactory(
                        dataset=public_dataset, sample=interval.site
                    ),
                )

        constant_query_count(build, lambda: client.get(CHILDREN, {"page_size": 100}))

    def test_a_site_nests_its_children_with_their_site_and_location(
        self, client, full_records
    ):
        record = detail(client, SITES, full_records["site"])

        child = record["intervals"][0]["children"][0]
        assert child["site"]["uuid"] == full_records["site"].uuid
        assert child["location"]["type"] == "Point"


@pytest.mark.django_db
class TestHeatFlowSerializer:
    @pytest.fixture
    def corrected(self, full_records):
        child = full_records["child"]
        HeatFlowCorrectionFactory(
            heat_flow=child,
            correction_type=CORRECTION_TYPES.IS,
            status=CORRECTION_STATUSES.PRESENT_CORRECTED,
            comment="Corrected for in-situ conditions.",
        )
        HeatFlowCorrectionFactory(
            heat_flow=child,
            correction_type=CORRECTION_TYPES.T,
            status=CORRECTION_STATUSES.NOT_CORRECTED,
        )
        return full_records

    def test_the_single_child_nests_its_gradient_and_conductivity_whole(
        self, client, full_records
    ):
        record = detail(client, CHILDREN, full_records["child"])

        assert record["thermal_gradient"]["uuid"] == full_records["gradient"].uuid
        assert record["thermal_gradient"]["value"] == 25.5
        assert record["thermal_gradient"]["units"]["value"] == "K/km"
        assert record["thermal_conductivity"]["value"] == 2.5
        assert record["thermal_conductivity"]["units"]["value"] == "W/mK"

    def test_every_correction_is_listed_with_its_type_and_status(
        self, client, corrected
    ):
        record = detail(client, CHILDREN, corrected["child"])

        by_type = {
            entry["correction_type"]["name"]: entry for entry in record["corrections"]
        }
        assert by_type[CORRECTION_TYPES.IS.value] == {
            "correction_type": {
                "name": CORRECTION_TYPES.IS.value,
                "label": CORRECTION_TYPES.IS.label,
            },
            "status": {
                "name": CORRECTION_STATUSES.PRESENT_CORRECTED.value,
                "label": CORRECTION_STATUSES.PRESENT_CORRECTED.label,
            },
            "comment": "Corrected for in-situ conditions.",
        }
        assert by_type[CORRECTION_TYPES.T.value]["comment"] is None

    def test_a_correction_not_applied_is_listed_and_an_unrecorded_type_is_absent(
        self, client, corrected
    ):
        record = detail(client, CHILDREN, corrected["child"])

        statuses = {
            entry["correction_type"]["name"]: entry["status"]["name"]
            for entry in record["corrections"]
        }
        assert statuses == {
            CORRECTION_TYPES.IS.value: CORRECTION_STATUSES.PRESENT_CORRECTED.value,
            CORRECTION_TYPES.T.value: CORRECTION_STATUSES.NOT_CORRECTED.value,
        }

    def test_a_child_with_no_gradient_conductivity_or_corrections_is_not_dropped(
        self, client, public_dataset
    ):
        child = HeatFlowFactory(dataset=public_dataset)

        record = detail(client, CHILDREN, child)

        assert record["thermal_gradient"] is None
        assert record["thermal_conductivity"] is None
        assert record["corrections"] == []

    def test_a_hidden_gradient_and_conductivity_are_null_on_the_single_child(
        self, client, full_records, private_dataset
    ):
        hide(full_records["gradient"], private_dataset)
        hide(full_records["conductivity"], private_dataset)

        record = detail(client, CHILDREN, full_records["child"])

        assert record["thermal_gradient"] is None
        assert record["thermal_conductivity"] is None

    def test_a_hidden_site_is_null_as_site_and_location_on_the_single_child(
        self, client, full_records, private_dataset
    ):
        visible = detail(client, CHILDREN, full_records["child"])
        hide(full_records["site"], private_dataset)
        hidden = detail(client, CHILDREN, full_records["child"])

        assert visible["site"]["uuid"] == full_records["site"].uuid
        assert visible["location"]["type"] == "Point"
        assert hidden["site"] is None
        assert hidden["location"] is None

    def test_a_single_child_costs_the_same_with_more_corrections(
        self, client, public_dataset, constant_query_count
    ):
        child = HeatFlowFactory(dataset=public_dataset)
        types = iter(CORRECTION_TYPES.values)

        def build(count):
            for _ in range(count):
                HeatFlowCorrectionFactory(heat_flow=child, correction_type=next(types))

        constant_query_count(
            build, lambda: client.get(f"{CHILDREN}{child.uuid}/"), low=1, high=3
        )


STORED_SCORE = {"score": 0.7, "score_missing": True, "quality_scheme": "hfqa_tool 0.2"}


@pytest.mark.django_db
class TestPlacedAtSite:
    @pytest.mark.parametrize("kind", ["interval", "gradient", "conductivity", "parent"])
    def test_a_record_carries_its_sites_coordinates_and_a_reference_to_it(
        self, client, full_records, kind
    ):
        site = full_records["site"]

        record = only_record(client, ROUTES[kind])

        assert record["location"]["type"] == "Point"
        assert record["location"]["coordinates"][:2] == [
            site.location.x,
            site.location.y,
        ]
        assert record["site"]["uuid"] == site.uuid
        assert record["site"]["url"].endswith(f"{SITES}{site.uuid}/")

    @pytest.mark.parametrize("kind", ["interval", "gradient", "conductivity", "parent"])
    def test_a_record_whose_site_is_hidden_has_no_location_and_no_site(
        self, client, full_records, private_dataset, kind
    ):
        hide(full_records["site"], private_dataset)

        record = only_record(client, ROUTES[kind])

        assert record["location"] is None
        assert record["site"] is None

    @pytest.mark.parametrize("kind", ["interval", "gradient", "conductivity"])
    def test_a_single_record_whose_site_is_hidden_has_no_location_and_no_site(
        self, client, full_records, private_dataset, kind
    ):
        visible = detail(client, ROUTES[kind], full_records[kind])
        hide(full_records["site"], private_dataset)
        hidden = detail(client, ROUTES[kind], full_records[kind])

        assert visible["site"]["uuid"] == full_records["site"].uuid
        assert visible["location"]["type"] == "Point"
        assert hidden["site"] is None
        assert hidden["location"] is None

    def test_a_site_nests_its_intervals_with_their_site_and_location(
        self, client, full_records
    ):
        record = detail(client, SITES, full_records["site"])

        interval = record["intervals"][0]
        assert interval["site"]["uuid"] == full_records["site"].uuid
        assert interval["location"]["type"] == "Point"

    @pytest.mark.parametrize("kind", ["interval", "gradient", "conductivity", "parent"])
    def test_the_list_costs_the_same_for_one_record_as_for_several(
        self, client, public_dataset, constant_query_count, kind
    ):
        def build(count):
            for _ in range(count):
                interval = HeatFlowIntervalFactory(dataset=public_dataset)
                if kind == "gradient":
                    ThermalGradientFactory(dataset=public_dataset, sample=interval)
                elif kind == "conductivity":
                    IntervalConductivityFactory(dataset=public_dataset, sample=interval)
                elif kind == "parent":
                    ParentHeatFlowFactory(dataset=public_dataset, sample=interval.site)

        constant_query_count(
            build, lambda: client.get(ROUTES[kind], {"page_size": 100})
        )


@pytest.mark.django_db
class TestHeatFlowIntervalSerializer:
    def test_the_single_interval_carries_its_probe_metadata_with_terms_and_units(
        self, client, full_records
    ):
        interval = full_records["interval"]
        probe = ProbeMetadataFactory(interval=interval)
        probe.refresh_from_db()

        record = detail(client, INTERVALS, interval)

        metadata = record["probe_metadata"]
        assert metadata["penetration"] == pytest.approx(
            float(probe.penetration.magnitude)
        )
        assert metadata["length"] == pytest.approx(float(probe.length.magnitude))
        assert metadata["tilt"] == pytest.approx(float(probe.tilt.magnitude))
        assert metadata["units"] == {"penetration": "m", "length": "m", "tilt": "deg"}
        assert [entry["name"] for entry in metadata["probe_type"]] == [
            concept.name for concept in probe.probe_type.order_by("name")
        ]
        assert set(metadata["probe_type"][0]) == {"name", "label", "uri", "vocabulary"}

    def test_an_interval_without_probe_metadata_carries_null(
        self, client, full_records
    ):
        record = detail(client, INTERVALS, full_records["interval"])

        assert record["probe_metadata"] is None

    def test_the_single_interval_refers_to_each_child_gradient_and_conductivity(
        self, client, full_records, public_dataset
    ):
        interval = full_records["interval"]
        other = IntervalConductivityFactory(dataset=public_dataset, sample=interval)

        record = detail(client, INTERVALS, interval)

        assert uuids(record["children"]) == {full_records["child"].uuid}
        assert uuids(record["thermal_gradients"]) == {full_records["gradient"].uuid}
        assert uuids(record["thermal_conductivities"]) == {
            full_records["conductivity"].uuid,
            other.uuid,
        }
        assert record["children"][0]["url"].endswith(
            f"{CHILDREN}{full_records['child'].uuid}/"
        )

    @pytest.mark.parametrize(
        ("kind", "entries"),
        [
            ("child", "children"),
            ("gradient", "thermal_gradients"),
            ("conductivity", "thermal_conductivities"),
        ],
    )
    def test_a_hidden_related_record_is_absent_from_the_lists(
        self, client, full_records, private_dataset, kind, entries
    ):
        hide(full_records[kind], private_dataset)

        record = detail(client, INTERVALS, full_records["interval"])

        assert record[entries] == []

    def test_the_interval_list_carries_no_related_lists_and_no_probe_metadata(
        self, client, full_records
    ):
        record = only_record(client, INTERVALS)

        for name in (
            "children",
            "thermal_gradients",
            "thermal_conductivities",
            "probe_metadata",
        ):
            assert name not in record

    def test_a_single_interval_costs_the_same_with_more_related_records(
        self, client, public_dataset, constant_query_count
    ):
        interval = HeatFlowIntervalFactory(dataset=public_dataset)
        ProbeMetadataFactory(interval=interval)

        def build(count):
            for _ in range(count):
                HeatFlowFactory(dataset=public_dataset, sample=interval)
                ThermalGradientFactory(dataset=public_dataset, sample=interval)
                IntervalConductivityFactory(dataset=public_dataset, sample=interval)

        constant_query_count(build, lambda: client.get(f"{INTERVALS}{interval.uuid}/"))


@pytest.mark.django_db
class TestThermalGradientSerializer:
    def test_a_scored_gradient_carries_its_stored_score(self, client, full_records):
        gradient = full_records["gradient"]
        type(gradient).objects.filter(pk=gradient.pk).update(**STORED_SCORE)

        record = only_record(client, GRADIENTS)

        assert {name: record[name] for name in STORED_SCORE} == STORED_SCORE

    def test_an_undetermined_score_is_null(self, client, full_records):
        gradient = full_records["gradient"]
        type(gradient).objects.filter(pk=gradient.pk).update(score=None)

        record = only_record(client, GRADIENTS)

        assert record["score"] is None

    def test_the_gradient_carries_its_temperatures_with_their_units(
        self, client, full_records
    ):
        gradient = full_records["gradient"]
        type(gradient).objects.filter(pk=gradient.pk).update(
            temperature_top=12.5,
            temperature_bottom=48.25,
            temperature_top_uncertainty=0.5,
            temperature_bottom_uncertainty=0.75,
        )

        record = only_record(client, GRADIENTS)

        assert record["temperature_top"] == 12.5
        assert record["temperature_bottom"] == 48.25
        assert record["temperature_top_uncertainty"] == 0.5
        assert record["temperature_bottom_uncertainty"] == 0.75
        assert {
            "temperature_top",
            "temperature_bottom",
            "temperature_top_uncertainty",
            "temperature_bottom_uncertainty",
        } <= set(record["units"])

    def test_the_single_gradient_refers_to_each_child_calculated_from_it(
        self, client, full_records, public_dataset
    ):
        gradient = full_records["gradient"]
        second = HeatFlowFactory(
            dataset=public_dataset,
            sample=full_records["interval"],
            thermal_gradient=gradient,
        )

        record = detail(client, GRADIENTS, gradient)

        assert uuids(record["children"]) == {full_records["child"].uuid, second.uuid}
        assert all(entry["url"] for entry in record["children"])

    def test_a_hidden_child_is_absent_from_the_gradients_children(
        self, client, full_records, private_dataset
    ):
        hide(full_records["child"], private_dataset)

        record = detail(client, GRADIENTS, full_records["gradient"])

        assert record["children"] == []

    def test_the_gradient_list_carries_no_children(self, client, full_records):
        assert "children" not in only_record(client, GRADIENTS)

    def test_a_single_gradient_costs_the_same_with_more_children(
        self, client, public_dataset, constant_query_count
    ):
        gradient = ThermalGradientFactory(dataset=public_dataset)

        def build(count):
            for _ in range(count):
                HeatFlowFactory(
                    dataset=public_dataset,
                    sample=gradient.sample,
                    thermal_gradient=gradient,
                )

        constant_query_count(build, lambda: client.get(f"{GRADIENTS}{gradient.uuid}/"))


@pytest.mark.django_db
class TestIntervalConductivitySerializer:
    def test_a_scored_conductivity_carries_its_stored_score(self, client, full_records):
        conductivity = full_records["conductivity"]
        type(conductivity).objects.filter(pk=conductivity.pk).update(**STORED_SCORE)

        record = only_record(client, CONDUCTIVITIES)

        assert {name: record[name] for name in STORED_SCORE} == STORED_SCORE

    def test_an_undetermined_score_is_null(self, client, full_records):
        conductivity = full_records["conductivity"]
        type(conductivity).objects.filter(pk=conductivity.pk).update(score=None)

        record = only_record(client, CONDUCTIVITIES)

        assert record["score"] is None

    def test_the_conductivity_carries_its_location_terms_and_number(
        self, client, full_records
    ):
        conductivity = full_records["conductivity"]
        concepts = list(
            Concept.get_for_vocabulary(
                IntervalConductivity._meta.get_field("conductivity_location").vocabulary
            ).order_by("name")[:2]
        )
        conductivity.conductivity_location.set(concepts)
        type(conductivity).objects.filter(pk=conductivity.pk).update(number=7)

        record = only_record(client, CONDUCTIVITIES)

        assert {entry["name"] for entry in record["conductivity_location"]} == {
            concept.name for concept in concepts
        }
        assert record["number"] == 7

    def test_the_single_conductivity_refers_to_each_child_calculated_from_it(
        self, client, full_records, public_dataset
    ):
        conductivity = full_records["conductivity"]
        second = HeatFlowFactory(
            dataset=public_dataset,
            sample=full_records["interval"],
            thermal_conductivity=conductivity,
        )

        record = detail(client, CONDUCTIVITIES, conductivity)

        assert uuids(record["children"]) == {full_records["child"].uuid, second.uuid}

    def test_a_hidden_child_is_absent_from_the_conductivitys_children(
        self, client, full_records, private_dataset
    ):
        hide(full_records["child"], private_dataset)

        record = detail(client, CONDUCTIVITIES, full_records["conductivity"])

        assert record["children"] == []

    def test_the_conductivity_list_carries_no_children(self, client, full_records):
        assert "children" not in only_record(client, CONDUCTIVITIES)

    def test_a_single_conductivity_costs_the_same_with_more_children(
        self, client, public_dataset, constant_query_count
    ):
        conductivity = IntervalConductivityFactory(dataset=public_dataset)

        def build(count):
            for _ in range(count):
                HeatFlowFactory(
                    dataset=public_dataset,
                    sample=conductivity.sample,
                    thermal_conductivity=conductivity,
                )

        constant_query_count(
            build, lambda: client.get(f"{CONDUCTIVITIES}{conductivity.uuid}/")
        )


@pytest.mark.django_db
class TestScoredMeasurementWrites:
    SUPPLIED = {"score": 1.2, "score_missing": True, "quality_scheme": "BOGUS"}

    @pytest.mark.parametrize(
        ("route", "model"),
        [(GRADIENTS, ThermalGradient), (CONDUCTIVITIES, IntervalConductivity)],
    )
    def test_a_create_supplying_a_score_stores_the_portals_own(
        self, editor, public_dataset, route, model
    ):
        interval = HeatFlowIntervalFactory(dataset=public_dataset)
        body = {"dataset": public_dataset.uuid, "sample": interval.uuid, "value": 2.5}

        for name, supplied in (("Plain", {}), ("Supplied", self.SUPPLIED)):
            response = editor.post(
                route,
                {"name": name, **body, **supplied},
                content_type="application/json",
            )
            assert response.status_code == 201, response.content

        plain = model.objects.get(name="Plain")
        written = model.objects.get(name="Supplied")
        assert written.quality_scheme != "BOGUS"
        assert {name: getattr(written, name) for name in STORED_SCORE} == {
            name: getattr(plain, name) for name in STORED_SCORE
        }

    @pytest.mark.parametrize(
        ("route", "factory"),
        [
            (GRADIENTS, ThermalGradientFactory),
            (CONDUCTIVITIES, IntervalConductivityFactory),
        ],
    )
    def test_an_update_supplying_a_score_stores_the_portals_own(
        self, editor, public_dataset, route, factory
    ):
        record = factory(dataset=public_dataset)
        url = f"{route}{record.uuid}/"
        editor.patch(url, {"name": "Plain"}, content_type="application/json")
        record.refresh_from_db()
        calculated = {name: getattr(record, name) for name in STORED_SCORE}

        response = editor.patch(
            url, {"name": "Supplied", **self.SUPPLIED}, content_type="application/json"
        )

        assert response.status_code == 200, response.content
        record.refresh_from_db()
        assert record.name == "Supplied"
        assert {name: getattr(record, name) for name in STORED_SCORE} == calculated
        assert record.quality_scheme != "BOGUS"


@pytest.mark.django_db
class TestHeatFlowChildWrites:
    SUPPLIED = {
        "U_score": "U4",
        "M_score": "M1",
        "T_score": 1.2,
        "T_score_missing": True,
        "TC_score": 1.2,
        "TC_score_missing": True,
        "quality": "BOGUS",
        "quality_scheme": "BOGUS",
        "ghfdb_id": 987654,
        "is_relevant": True,
    }

    def test_a_create_supplying_scores_and_an_identifier_stores_none_of_them(
        self, editor, public_dataset
    ):
        interval = HeatFlowIntervalFactory(dataset=public_dataset)

        response = editor.post(
            CHILDREN,
            {
                "name": "Written child",
                "dataset": public_dataset.uuid,
                "sample": interval.uuid,
                "value": 61.5,
                "method": [],
                **self.SUPPLIED,
            },
            content_type="application/json",
        )

        assert response.status_code == 201, response.content
        child = HeatFlow.objects.get(name="Written child")
        assert child.ghfdb_id is None
        assert child.quality != "BOGUS"
        assert child.quality_scheme != "BOGUS"
        assert (child.U_score, child.M_score) == ("Ux", "Mx")
        assert (child.T_score, child.TC_score) == (None, None)
        assert (child.T_score_missing, child.TC_score_missing) == (False, False)
        assert child.is_relevant is False

    @pytest.mark.parametrize(
        ("route", "factory"),
        [
            (GRADIENTS, ThermalGradientFactory),
            (CONDUCTIVITIES, IntervalConductivityFactory),
            (PARENTS, ParentHeatFlowFactory),
        ],
    )
    def test_an_update_of_a_measurement_placed_on_its_sample_is_saved(
        self, editor, public_dataset, route, factory
    ):
        record = factory(dataset=public_dataset)

        response = editor.patch(
            f"{route}{record.uuid}/",
            {"name": "Renamed"},
            content_type="application/json",
        )

        assert response.status_code == 200, response.content
        record.refresh_from_db()
        assert record.name == "Renamed"

    def test_an_update_supplying_scores_and_an_identifier_stores_none_of_them(
        self, editor, public_dataset
    ):
        child = HeatFlowFactory(dataset=public_dataset, value=70, uncertainty=3.5)
        child.refresh_from_db()
        stored = {name: getattr(child, name) for name in (*SCORES, "ghfdb_id")}

        response = editor.patch(
            f"{CHILDREN}{child.uuid}/",
            {"expedition": "Cruise 7", **self.SUPPLIED},
            content_type="application/json",
        )

        assert response.status_code == 200, response.content
        child.refresh_from_db()
        assert child.expedition == "Cruise 7"
        assert {name: getattr(child, name) for name in stored} == stored
        assert child.is_relevant is False
        assert all(stored[name] != self.SUPPLIED[name] for name in stored)
