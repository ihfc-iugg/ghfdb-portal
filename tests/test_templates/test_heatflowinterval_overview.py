# Tests for the depth interval's overview page, the site's location shown on every page
# made on an interval, FairDM's shared page on all six heat flow types, and the release
# columns (SC-001). Read through the pages' URLs; the content is found by the ``data-``
# hooks the templates carry, never by wording. Mirrors no Python module: the subject is
# the templates under ``project/heat_flow/templates/`` and ``templates/cotton/``,
# declared under ``non-mirror-paths`` in pyproject.toml.

import pytest
from fairdm.core.sample.models import SampleIdentifier
from fairdm.core.vocabularies import IGSN
from heat_flow import vocabularies
from heat_flow.models import HeatFlowInterval, HeatFlowSite

from project.ghfdb.resources.export import GHFDBExportResource
from tests.factories import ProbeMetadataFactory

pytestmark = pytest.mark.django_db

# The page each column of the release format is read on, and the ``data-field`` it is
# found by there. Mirrors the column-to-page table in ``docs/guides/record-pages.md``.
# The columns themselves come from the export resource, never from this table.
RELEASE_COLUMNS = {
    "q": ("parent", "value"),
    "q_uncertainty": ("parent", "value"),
    "name": ("interval", "site"),
    "lat_ns": ("child", "location"),
    "long_ew": ("child", "location"),
    "elevation": ("site", "elevation"),
    "environment": ("site", "environment"),
    "p_comment": ("parent", "comment"),
    "corr_hp_flag": ("parent", "corr_HP_flag"),
    "total_depth_md": ("site", "length"),
    "total_depth_tvd": ("site", "vertical_depth"),
    "explo_method": ("site", "explo_method"),
    "explo_purpose": ("site", "explo_purpose"),
    "id": ("child", "ghfdb_id"),
    "qc": ("child", "value"),
    "qc_uncertainty": ("child", "value"),
    "q_method": ("child", "method"),
    "q_top": ("interval", "depth_range"),
    "q_bottom": ("interval", "depth_range"),
    "probe_penetration": ("interval", "probe_penetration"),
    "publication_reference": ("child", "publication_reference"),
    "data_reference": ("child", "data_reference"),
    "relevant_child": ("child", "is_relevant"),
    "c_comment": ("child", "comment"),
    "corr_is_flag": ("child", "corrections"),
    "corr_t_flag": ("child", "corrections"),
    "corr_s_flag": ("child", "corrections"),
    "corr_e_flag": ("child", "corrections"),
    "corr_topo_flag": ("child", "corrections"),
    "corr_pal_flag": ("child", "corrections"),
    "corr_sur_flag": ("child", "corrections"),
    "corr_conv_flag": ("child", "corrections"),
    "corr_hr_flag": ("child", "corrections"),
    "expedition": ("child", "expedition"),
    "probe_type": ("interval", "probe_type"),
    "probe_length": ("interval", "probe_length"),
    "probe_tilt": ("interval", "probe_tilt"),
    "water_temperature": ("child", "surface_temperature"),
    "geo_lithology": ("interval", "lithology"),
    "geo_stratigraphy": ("interval", "stratigraphy"),
    "t_grad_mean": ("gradient", "value"),
    "t_grad_uncertainty": ("gradient", "value"),
    "t_grad_mean_cor": ("gradient", "corrected_value"),
    "t_grad_uncertainty_cor": ("gradient", "corrected_value"),
    "t_method_top": ("gradient", "method_top"),
    "t_method_bottom": ("gradient", "method_bottom"),
    "t_shutin_top": ("gradient", "shutin_top"),
    "t_shutin_bottom": ("gradient", "shutin_bottom"),
    "t_corr_top": ("gradient", "correction_top"),
    "t_corr_bottom": ("gradient", "correction_bottom"),
    "t_number": ("gradient", "number"),
    "q_date": ("child", "date_acquired"),
    "tc_mean": ("conductivity", "value"),
    "tc_uncertainty": ("conductivity", "value"),
    "tc_source": ("conductivity", "source"),
    "tc_location": ("conductivity", "conductivity_location"),
    "tc_method": ("conductivity", "method"),
    "tc_saturation": ("conductivity", "saturation"),
    "tc_pt_conditions": ("conductivity", "pT_conditions"),
    "tc_pt_function": ("conductivity", "pT_function"),
    "tc_number": ("conductivity", "number"),
    "tc_strategy": ("conductivity", "strategy"),
    "ref_igsn": ("interval", "igsn"),
}
# The columns the resource writes: those its canonical order names that it carries a
# field for. Compared ignoring case, as the resource spells some of them with capitals.
EXPORTED_COLUMNS = sorted(
    column.lower()
    for column in GHFDBExportResource.Meta.export_order
    if column.lower() in {field.lower() for field in GHFDBExportResource.fields}
)
PAGES = ("site", "interval", "child", "gradient", "conductivity", "parent")
PAGES_ON_AN_INTERVAL = ("interval", "child", "gradient", "conductivity", "parent")


def link_to(node, record):
    """Say whether ``node`` links to ``record``'s page."""
    return record.get_absolute_url() in node.hrefs


def a_term_of(record, field_name):
    """One concept of the vocabulary ``record``'s field declares."""
    vocabulary = type(record)._meta.get_field(field_name).vocabulary[0]
    return vocabularies.concepts(vocabulary).first()


def shows_term(node, concept):
    """Say whether ``node`` shows a vocabulary concept's label, in any case.

    The page may capitalise the first letter.
    """
    return concept.display_label().casefold() in node.text.casefold()


@pytest.fixture
def records(page_records):
    """A child page's records, with probe metadata and an IGSN on the interval."""
    interval = page_records["interval"]
    ProbeMetadataFactory(interval=interval, length=5, penetration=3, tilt=2)
    SampleIdentifier.objects.create(
        related=interval, type_id=IGSN, value="10.60510/IEGHFTEST01"
    )
    return page_records


def set_location(site, location=None):
    """Replace ``site``'s location in the database, or clear it with ``None``."""
    HeatFlowSite.objects.filter(pk=site.pk).update(location=location)
    site.refresh_from_db()


class TestIntervalPage:
    def test_it_shows_its_depth_range_lithology_and_age(self, document, records):
        interval = records["interval"]
        lithology = a_term_of(interval, "lithology")
        age = a_term_of(interval, "age")
        interval.lithology.set([lithology])
        interval.age.set([age])

        page = document(interval)

        depth = page.find("data-field", "depth_range").text
        assert str(interval.top) in depth
        assert str(interval.bottom) in depth
        assert shows_term(page.find("data-field", "lithology"), lithology)
        assert shows_term(page.find("data-field", "age"), age)

    def test_an_interval_with_no_stratigraphy_says_it_is_not_recorded(
        self, document, records
    ):
        page = document(records["interval"])

        field = page.find("data-field", "stratigraphy")
        assert field.attrs["data-state"] == "not-recorded"

    def test_it_links_to_its_site(self, document, records):
        page = document(records["interval"])

        assert link_to(page.find("data-heat-flow", "site"), records["site"])

    def test_a_site_in_an_unpublished_dataset_is_neither_named_nor_linked(
        self, document, records, hide
    ):
        hide(records["site"])

        page = document(records["interval"])

        site = page.find("data-heat-flow", "site")
        assert site.attrs["data-state"] == "hidden"
        assert site.hrefs == []
        assert page.find("data-field", "site").attrs["data-state"] == "not-recorded"

    def test_it_shows_the_probe_type_length_penetration_and_tilt(
        self, document, records
    ):
        interval = HeatFlowInterval.objects.get(pk=records["interval"].pk)
        probe = interval.probe_metadata
        concept = a_term_of(probe, "probe_type")
        probe.probe_type.set([concept])

        page = document(interval)

        card = page.find("data-heat-flow", "probe")
        assert shows_term(card.find("data-field", "probe_type"), concept)
        assert str(probe.length) in card.find("data-field", "probe_length").text
        assert (
            str(probe.penetration) in card.find("data-field", "probe_penetration").text
        )
        assert str(probe.tilt) in card.find("data-field", "probe_tilt").text

    def test_an_interval_without_probe_metadata_shows_no_probe_card(
        self, document, page_records
    ):
        assert (
            document(page_records["interval"]).find("data-heat-flow", "probe") is None
        )

    def test_it_shows_the_vertical_depth_and_datum(self, document, records):
        HeatFlowInterval.objects.filter(pk=records["interval"].pk).update(
            vertical_depth=480, vertical_datum="mean sea level"
        )
        interval = HeatFlowInterval.objects.get(pk=records["interval"].pk)

        page = document(interval)

        assert (
            str(interval.vertical_depth)
            in page.find("data-field", "vertical_depth").text
        )
        assert interval.vertical_datum in page.find("data-field", "vertical_datum").text

    def test_a_field_with_no_value_says_it_is_not_recorded(self, document, records):
        HeatFlowInterval.objects.filter(pk=records["interval"].pk).update(
            vertical_datum=""
        )

        page = document(HeatFlowInterval.objects.get(pk=records["interval"].pk))

        field = page.find("data-field", "vertical_datum")
        assert field.attrs["data-state"] == "not-recorded"

    def test_it_shows_the_igsn_recorded_for_the_interval(self, document, records):
        page = document(records["interval"])

        assert "10.60510/IEGHFTEST01" in page.find("data-field", "igsn").text

    def test_an_interval_without_an_igsn_says_it_is_not_recorded(
        self, document, page_records
    ):
        page = document(page_records["interval"])

        assert page.find("data-field", "igsn").attrs["data-state"] == "not-recorded"


class TestSiteLocationOnPages:
    @pytest.mark.parametrize("name", PAGES_ON_AN_INTERVAL)
    def test_the_page_shows_the_sites_coordinates_as_the_sites(
        self, document, records, name
    ):
        site = records["site"]

        page = document(records[name])

        place = page.find("data-heat-flow", "location")
        assert place.attrs["data-source"] == "site"
        assert "data-state" not in place.attrs
        map_ = place.find("data-lon")
        assert float(map_.attrs["data-lon"]) == pytest.approx(site.location.x)
        assert float(map_.attrs["data-lat"]) == pytest.approx(site.location.y)

    @pytest.mark.parametrize("name", PAGES_ON_AN_INTERVAL)
    def test_a_site_without_a_location_says_none_is_recorded(
        self, document, records, name
    ):
        set_location(records["site"])

        page = document(records[name])

        place = page.find("data-heat-flow", "location")
        assert place.attrs["data-state"] == "not-recorded"
        assert place.find("data-lon") is None

    @pytest.mark.parametrize("name", PAGES_ON_AN_INTERVAL)
    def test_a_site_in_an_unpublished_dataset_shows_no_location(
        self, document, records, hide, name
    ):
        hide(records["site"])

        page = document(records[name])

        place = page.find("data-heat-flow", "location")
        assert place.attrs["data-state"] == "hidden"
        assert place.find("data-lon") is None


class TestRecordPagesKeepFairDMsPage:
    @pytest.mark.parametrize("name", PAGES)
    def test_it_keeps_the_identifiers_and_citation_cards(self, document, records, name):
        page = document(records[name])

        assert page.find("data-card", "identifiers") is not None
        assert page.find("data-card", "citation") is not None

    @pytest.mark.parametrize("name", PAGES)
    def test_a_visitor_is_not_shown_the_manage_menu(self, document, records, name):
        assert document(records[name]).find("data-menu", "manage") is None


class TestReleaseColumns:
    @pytest.mark.parametrize("column", EXPORTED_COLUMNS)
    def test_every_column_the_export_writes_is_found_on_its_page(
        self, document, records, column
    ):
        assert column in RELEASE_COLUMNS, f"{column} has no page in the table"
        name, field = RELEASE_COLUMNS[column]

        page = document(records[name])

        assert page.find("data-field", field) is not None

    def test_the_table_names_no_column_the_export_does_not_write(self):
        assert set(RELEASE_COLUMNS) <= set(EXPORTED_COLUMNS)
