"""Tests for GHFDB admin changelist configuration and rendering (T013, T063, T066)."""

import pytest
from django.contrib import admin
from django.urls import reverse

from project.ghfdb.admin import ExplorePurposeListFilter
from project.ghfdb.models import GHFDB

EXPECTED_LIST_DISPLAY = (
    "get_id_parent",
    "get_q",
    "get_q_uncertainty",
    "get_name",
    "get_lat_ns",
    "get_long_ew",
    "get_elevation",
    "get_environment",
    "get_corr_hp_flag",
    "get_total_depth_md",
    "get_total_depth_tvd",
    "get_explo_method",
    "get_explo_purpose",
    "get_country",
    "get_region",
    "get_continent",
    "get_domain",
)

EXPECTED_HEADERS = [
    "ID_parent",
    "q",
    "q_uncertainty",
    "name",
    "lat_NS",
    "long_EW",
    "elevation",
    "environment",
    "corr_HP_flag",
    "total_depth_MD",
    "total_depth_TVD",
    "explo_method",
    "explo_purpose",
    "country",
    "region",
    "continent",
    "domain",
]

EXPECTED_SEARCH_FIELDS = (
    "sample__heatflowinterval__sample__name",
    "parent__local_id",
)

EXPECTED_LIST_FILTER = (
    "sample__heatflowinterval__sample__heatflowsite__environment",
    "parent__corr_HP_flag",
    "sample__heatflowinterval__sample__heatflowsite__explo_method",
    ExplorePurposeListFilter,
    "sample__heatflowinterval__sample__heatflowsite__country",
    "sample__heatflowinterval__sample__heatflowsite__region",
    "sample__heatflowinterval__sample__heatflowsite__continent",
    "sample__heatflowinterval__sample__heatflowsite__domain",
)


@pytest.mark.django_db
def test_ghfdb_admin_changelist_refined_configuration(admin_client, heat_flow_chain):
    """T013: Changelist renders and exposes refined ordered columns/search/filters."""
    url = reverse("admin:ghfdb_ghfdb_changelist")
    response = admin_client.get(url)
    assert response.status_code == 200

    model_admin = admin.site._registry[GHFDB]
    assert model_admin.list_display == EXPECTED_LIST_DISPLAY
    assert model_admin.search_fields == EXPECTED_SEARCH_FIELDS
    assert model_admin.list_filter == EXPECTED_LIST_FILTER

    headers = [getattr(model_admin, name).short_description for name in EXPECTED_LIST_DISPLAY]
    assert headers == EXPECTED_HEADERS

    content = response.content.decode()
    assert "GHFDB Entries" in content


@pytest.mark.django_db
def test_ghfdb_admin_search_by_name_and_id_parent(admin_client, heat_flow_chain):
    """T013: Search works using parent ID and site name mapped fields."""
    entry = heat_flow_chain
    entry.parent.local_id = "PARENT-SEARCH-001"
    entry.parent.save(update_fields=["local_id"])

    url = reverse("admin:ghfdb_ghfdb_changelist")

    response_by_name = admin_client.get(url, {"q": entry.sample.heatflowinterval.sample.name})
    assert response_by_name.status_code == 200

    response_by_parent_id = admin_client.get(url, {"q": entry.parent.local_id})
    assert response_by_parent_id.status_code == 200


@pytest.mark.django_db
def test_explo_purpose_filter_choices_are_vocabulary_scoped(admin_client, heat_flow_chain):
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
    f = ExplorePurposeListFilter(request=None, params={}, model=GHFDB, model_admin=model_admin)
    lookup_pks = {pk for pk, _label in f.lookups(None, model_admin)}

    # Vocabulary-scoped concepts
    vocab_pks = set(Concept.get_for_vocabulary(ExplorationPurpose).values_list("pk", flat=True))

    # All lookup pks must belong to the ExplorationPurpose vocabulary
    assert lookup_pks, "lookups() must return at least one choice"
    assert lookup_pks.issubset(vocab_pks), (
        f"Filter choices contain concepts outside the ExplorationPurpose vocabulary: {lookup_pks - vocab_pks}"
    )

    # No unrelated concept (from a different vocabulary) should appear in lookup choices
    all_concept_pks = set(Concept.objects.values_list("pk", flat=True))
    non_vocab_pks = all_concept_pks - vocab_pks
    overlap = lookup_pks & non_vocab_pks
    assert not overlap, f"Filter choices include {len(overlap)} non-ExplorationPurpose concept(s)"


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
    "get_corr_hp_flag",
    "get_total_depth_md",
    "get_total_depth_tvd",
    "get_explo_method",
    "get_explo_purpose",
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
    "corr_HP_flag",
    "total_depth_MD",
    "total_depth_TVD",
    "explo_method",
    "explo_purpose",
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
    display_methods = [m for m in PARENT_EXPECTED_LIST_DISPLAY if m not in ("total_children", "relevant_children")]
    headers = [getattr(model_admin, name).short_description for name in display_methods]
    assert headers == PARENT_EXPECTED_HEADERS

    content = response.content.decode()
    assert "GHFDB Parent Entries" in content


@pytest.mark.django_db
def test_ghfdb_parent_admin_import_resource_only(admin_client):
    """T071 (US1b): GHFDBParentAdmin.get_import_resource_classes() returns only
    GHFDBParentImportResource — no child or export resource attached."""
    from project.ghfdb.models import GHFDBParent
    from project.ghfdb.resources import GHFDBChildImportResource, GHFDBParentImportResource

    model_admin = admin.site._registry[GHFDBParent]
    resource_classes = model_admin.get_import_resource_classes(request=None)
    assert resource_classes == [GHFDBParentImportResource], (
        f"Expected [GHFDBParentImportResource], got {resource_classes}"
    )
    assert GHFDBChildImportResource not in resource_classes
