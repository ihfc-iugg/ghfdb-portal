"""Tests for GHFDB admin changelist configuration and rendering (T013, T063, T066)."""

import pytest
from django.contrib import admin
from django.test import RequestFactory
from django.urls import reverse

from project.ghfdb.admin import (
    ChildExplorationMethodListFilter,
    EnvironmentListFilter,
    ExplorePurposeListFilter,
    ParentEnvironmentListFilter,
    ParentExplorationMethodListFilter,
)
from project.ghfdb.models import GHFDB

EXPECTED_LIST_DISPLAY = (
    "ghfdb_id",
    "get_id_parent",
    "site_name",
    "lat_NS",
    "long_EW",
    "qc",
    "qc_uncertainty",
    "get_q_method",
    "q_top",
    "q_bottom",
    "probe_penetration",
    "get_publication_reference",
    "get_data_reference",
    "relevant_child",
    "c_comment",
    "corr_IS_flag",
    "corr_T_flag",
    "corr_S_flag",
    "corr_E_flag",
    "corr_TOPO_flag",
    "corr_PAL_flag",
    "corr_SUR_flag",
    "corr_CONV_flag",
    "corr_HR_flag",
    "expedition",
    "get_probe_type",
    "probe_length",
    "probe_tilt",
    "water_temperature",
    "get_geo_lithology",
    "get_geo_stratigraphy",
    "T_grad_mean",
    "T_grad_uncertainty",
    "T_grad_mean_cor",
    "T_grad_uncertainty_cor",
    "get_t_method_top",
    "get_t_method_bottom",
    "T_shutin_top",
    "T_shutin_bottom",
    "get_t_corr_top",
    "get_t_corr_bottom",
    "T_number",
    "q_date",
    "tc_mean",
    "tc_uncertainty",
    "get_tc_source",
    "get_tc_location",
    "get_tc_method",
    "get_tc_saturation",
    "get_tc_p_t_conditions",
    "get_tc_p_t_fuction",
    "tc_number",
    "get_tc_strategy",
    "get_quality",
    "get_ref_isgn",
)

EXPECTED_SEARCH_FIELDS = (
    "sample__heatflowinterval__sample__name",
    "parent__ghfdb_id",
    "ghfdb_id",
)

EXPECTED_LIST_FILTER = (
    EnvironmentListFilter,
    "parent__corr_HP_flag",
    ChildExplorationMethodListFilter,
    ExplorePurposeListFilter,
    "sample__heatflowinterval__sample__heatflowsite__country",
    "sample__heatflowinterval__sample__heatflowsite__region",
    "sample__heatflowinterval__sample__heatflowsite__continent",
    "sample__heatflowinterval__sample__heatflowsite__domain",
)


@pytest.mark.django_db
def test_ghfdb_admin_changelist_refined_configuration(admin_client, heat_flow_chain):
    """T013: Changelist renders and exposes refined ordered columns/search/filters."""
    from project.ghfdb.resources import (
        GHFDBChildImportResource,
        GHFDBExportResource,
        GHFDBParentImportResource,
    )

    url = reverse("admin:ghfdb_ghfdb_changelist")
    response = admin_client.get(url)
    assert response.status_code == 200

    model_admin = admin.site._registry[GHFDB]
    assert model_admin.list_display == EXPECTED_LIST_DISPLAY
    assert model_admin.search_fields == EXPECTED_SEARCH_FIELDS
    assert model_admin.list_filter == EXPECTED_LIST_FILTER
    assert model_admin.get_import_resource_classes(request=None) == [
        GHFDBChildImportResource
    ]
    assert GHFDBParentImportResource not in model_admin.get_import_resource_classes(
        request=None
    )
    assert model_admin.get_export_resource_classes(request=None) == [
        GHFDBExportResource
    ]

    content = response.content.decode()
    assert "GHFDB Children" in content


@pytest.mark.django_db
def test_ghfdb_admin_search_by_name_and_id_parent(admin_client, heat_flow_chain):
    """T013: Search works using parent ghfdb_id and site name mapped fields."""
    entry = heat_flow_chain
    entry.parent.ghfdb_id = 99999
    entry.parent.save(update_fields=["ghfdb_id"])

    url = reverse("admin:ghfdb_ghfdb_changelist")

    response_by_name = admin_client.get(
        url, {"q": entry.sample.heatflowinterval.sample.name}
    )
    assert response_by_name.status_code == 200

    response_by_parent_id = admin_client.get(url, {"q": str(entry.parent.ghfdb_id)})
    assert response_by_parent_id.status_code == 200


@pytest.mark.django_db
def test_explo_purpose_filter_choices_are_vocabulary_scoped(
    admin_client, heat_flow_chain
):
    """T063: explo_purpose list filter choices are restricted to ExplorationPurpose vocabulary.

    Verifies that ExplorePurposeListFilter.lookups() only returns concepts belonging to the
    ExplorationPurpose vocabulary, excluding unrelated generic Concept values.
    """
    from heat_flow.vocabularies import ExplorationPurpose
    from research_vocabs.models import Concept

    model_admin = admin.site._registry[GHFDB]

    # Confirm the filter class appears in list_filter (not raw string)
    assert ExplorePurposeListFilter in model_admin.list_filter, (
        "ExplorePurposeListFilter must be present in list_filter"
    )

    # Instantiate filter and collect lookup choices
    f = ExplorePurposeListFilter(
        request=None, params={}, model=GHFDB, model_admin=model_admin
    )
    lookup_pks = {pk for pk, _label in f.lookups(None, model_admin)}

    # Vocabulary-scoped concepts
    vocab_pks = set(
        Concept.get_for_vocabulary(ExplorationPurpose).values_list("pk", flat=True)
    )

    # All lookup pks must belong to the ExplorationPurpose vocabulary
    assert lookup_pks, "lookups() must return at least one choice"
    assert lookup_pks.issubset(vocab_pks), (
        f"Filter choices contain concepts outside the ExplorationPurpose vocabulary: {lookup_pks - vocab_pks}"
    )

    # No unrelated concept (from a different vocabulary) should appear in lookup choices
    all_concept_pks = set(Concept.objects.values_list("pk", flat=True))
    non_vocab_pks = all_concept_pks - vocab_pks
    overlap = lookup_pks & non_vocab_pks
    assert not overlap, (
        f"Filter choices include {len(overlap)} non-ExplorationPurpose concept(s)"
    )


@pytest.mark.django_db
def test_environment_filter_choices_are_vocabulary_scoped(admin_client):
    """BUG-004: EnvironmentListFilter.lookups() returns GeographicEnvironment vocabulary choices.

    Verifies that the filter shows human-readable vocabulary labels rather than
    raw stored concept keys, and that all returned choices are defined in the
    GeographicEnvironment vocabulary (FR-014, FR-015).
    """
    from heat_flow.vocabularies import GeographicEnvironment

    model_admin = admin.site._registry[GHFDB]
    assert EnvironmentListFilter in model_admin.list_filter, (
        "EnvironmentListFilter must be present in list_filter"
    )

    f = EnvironmentListFilter(
        request=None, params={}, model=GHFDB, model_admin=model_admin
    )
    lookup_values = {value for value, _label in f.lookups(None, model_admin)}
    vocab_values = {value for value, _label in GeographicEnvironment().choices}

    assert lookup_values, "lookups() must return at least one choice"
    assert lookup_values == vocab_values, (
        f"EnvironmentListFilter choices do not match GeographicEnvironment vocabulary: "
        f"extra={lookup_values - vocab_values}, missing={vocab_values - lookup_values}"
    )


@pytest.mark.django_db
def test_explo_method_filter_choices_are_vocabulary_scoped(admin_client):
    """BUG-004: ChildExplorationMethodListFilter.lookups() returns ExplorationMethod vocabulary choices.

    Verifies that the filter shows human-readable vocabulary labels rather than
    raw stored concept keys, and that all returned choices are defined in the
    ExplorationMethod vocabulary (FR-014, FR-015).
    """
    from heat_flow.vocabularies import ExplorationMethod

    model_admin = admin.site._registry[GHFDB]
    assert ChildExplorationMethodListFilter in model_admin.list_filter, (
        "ChildExplorationMethodListFilter must be present in list_filter"
    )

    f = ChildExplorationMethodListFilter(
        request=None, params={}, model=GHFDB, model_admin=model_admin
    )
    lookup_values = {value for value, _label in f.lookups(None, model_admin)}
    vocab_values = {value for value, _label in ExplorationMethod().choices}

    assert lookup_values, "lookups() must return at least one choice"
    assert lookup_values == vocab_values, (
        f"ChildExplorationMethodListFilter choices do not match ExplorationMethod vocabulary: "
        f"extra={lookup_values - vocab_values}, missing={vocab_values - lookup_values}"
    )


@pytest.mark.django_db
def test_parent_environment_filter_choices_are_vocabulary_scoped(admin_client):
    """BUG-004: ParentEnvironmentListFilter.lookups() returns GeographicEnvironment vocabulary choices."""
    from heat_flow.vocabularies import GeographicEnvironment

    from project.ghfdb.models import GHFDBParent

    model_admin = admin.site._registry[GHFDBParent]
    assert ParentEnvironmentListFilter in model_admin.list_filter, (
        "ParentEnvironmentListFilter must be present in GHFDBParentAdmin.list_filter"
    )

    f = ParentEnvironmentListFilter(
        request=None, params={}, model=GHFDBParent, model_admin=model_admin
    )
    lookup_values = {value for value, _label in f.lookups(None, model_admin)}
    vocab_values = {value for value, _label in GeographicEnvironment().choices}

    assert lookup_values, "lookups() must return at least one choice"
    assert lookup_values == vocab_values


@pytest.mark.django_db
def test_parent_explo_method_filter_choices_are_vocabulary_scoped(admin_client):
    """BUG-004: ParentExplorationMethodListFilter.lookups() returns ExplorationMethod vocabulary choices."""
    from heat_flow.vocabularies import ExplorationMethod

    from project.ghfdb.models import GHFDBParent

    model_admin = admin.site._registry[GHFDBParent]
    assert ParentExplorationMethodListFilter in model_admin.list_filter, (
        "ParentExplorationMethodListFilter must be present in GHFDBParentAdmin.list_filter"
    )

    f = ParentExplorationMethodListFilter(
        request=None, params={}, model=GHFDBParent, model_admin=model_admin
    )
    lookup_values = {value for value, _label in f.lookups(None, model_admin)}
    vocab_values = {value for value, _label in ExplorationMethod().choices}

    assert lookup_values, "lookups() must return at least one choice"
    assert lookup_values == vocab_values


@pytest.mark.django_db
def test_authenticated_staff_import_page_renders_http200(admin_client):
    """T066: Authenticated staff GET /admin/ghfdb/ghfdb/import/ returns HTTP 200.

    Regression for BUG-002: verifies that the django-import-export admin hook
    overrides use request-aware method signatures compatible with v4.x so the
    import page renders without a server error.
    """
    url = reverse("admin:ghfdb_ghfdb_import")
    response = admin_client.get(url)
    assert response.status_code == 200, (
        f"Import page returned {response.status_code}; expected 200. Check get_import_resource_classes() signature."
    )


@pytest.mark.django_db
def test_ghfdb_admin_queryset_evaluates_without_invalid_prefetch(
    admin_user, heat_flow_chain
):
    """T080 (BUG-003): Child admin queryset evaluates without invalid prefetch paths."""
    request = RequestFactory().get(reverse("admin:ghfdb_ghfdb_changelist"))
    request.user = admin_user

    model_admin = admin.site._registry[GHFDB]
    queryset = model_admin.get_queryset(request)

    rows = list(queryset)
    assert rows, "Expected at least one GHFDB child row in queryset evaluation"


# ---------------------------------------------------------------------------
# Phase 3b: GHFDBParent admin tests (T070–T071)
# ---------------------------------------------------------------------------

PARENT_EXPECTED_LIST_DISPLAY = (
    "get_id_parent",
    "get_q",
    "get_q_uncertainty",
    "get_name",
    "get_lat_ns",
    "get_long_ew",
    "get_elevation",
    "get_environment",
    "get_p_comment",
    "get_corr_hp_flag",
    "get_total_depth_md",
    "get_total_depth_tvd",
    "get_explo_method",
    "get_explo_purpose",
    "get_quality",
    "get_country",
    "get_region",
    "get_continent",
    "get_domain",
    "total_children",
    "relevant_children",
)

PARENT_EXPECTED_HEADERS = [
    "ID_parent",
    "q",
    "q_uncertainty",
    "name",
    "lat_NS",
    "long_EW",
    "elevation",
    "environment",
    "p_comment",
    "corr_HP_flag",
    "total_depth_MD",
    "total_depth_TVD",
    "explo_method",
    "explo_purpose",
    "quality",
    "country",
    "region",
    "continent",
    "domain",
]


@pytest.mark.django_db
def test_ghfdb_parent_admin_changelist(admin_client, heat_flow_chain):
    """T070 (US1b): GHFDBParentAdmin changelist renders with correct columns."""
    from project.ghfdb.models import GHFDBParent

    url = reverse("admin:ghfdb_ghfdbparent_changelist")
    response = admin_client.get(url)
    assert response.status_code == 200

    model_admin = admin.site._registry[GHFDBParent]
    assert model_admin.list_display == PARENT_EXPECTED_LIST_DISPLAY

    # Verify short_description headers for the non-computed display methods
    display_methods = [
        m
        for m in PARENT_EXPECTED_LIST_DISPLAY
        if m not in ("total_children", "relevant_children")
    ]
    headers = [getattr(model_admin, name).short_description for name in display_methods]
    assert headers == PARENT_EXPECTED_HEADERS

    content = response.content.decode()
    assert "GHFDB Parents" in content


@pytest.mark.django_db
def test_ghfdb_parent_admin_import_resource_only(admin_client):
    """T071 (US1b): GHFDBParentAdmin.get_import_resource_classes() returns only
    GHFDBParentImportResource — no child or export resource attached."""
    from project.ghfdb.models import GHFDBParent
    from project.ghfdb.resources import (
        GHFDBChildImportResource,
        GHFDBParentImportResource,
    )

    model_admin = admin.site._registry[GHFDBParent]
    resource_classes = model_admin.get_import_resource_classes(request=None)
    assert resource_classes == [GHFDBParentImportResource], (
        f"Expected [GHFDBParentImportResource], got {resource_classes}"
    )
    assert GHFDBChildImportResource not in resource_classes
