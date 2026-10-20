import pytest
from django.core.checks import run_checks
from fairdm.contrib.contributors.choices import ContributionLevel
from fairdm.factories import UserFactory
from heat_flow.models import HeatFlowSite
from research_vocabs.models import Concept

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
    "site": {"azimuth": "deg", "inclination": "deg", "length": "m"},
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
