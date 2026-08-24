"""Tests for GHFDB admin changelist configuration and rendering (T013, T063,
T066, T078-T089)."""

import pytest
from django.contrib import admin
from django.contrib.admin.templatetags.admin_list import result_headers
from django.contrib.admin.utils import label_for_field
from django.test import RequestFactory
from django.urls import reverse

from project.ghfdb.admin import (
    ChildExplorationMethodListFilter,
    EnvironmentListFilter,
    ExplorePurposeListFilter,
    ParentEnvironmentListFilter,
    ParentExplorationMethodListFilter,
)
from project.ghfdb.constants import CHILD_COLUMNS, PARENT_COLUMNS
from project.ghfdb.models import GHFDBChild

pytestmark = pytest.mark.ghfdb

EXPECTED_SEARCH_FIELDS = (
    "sample__heatflowinterval__site__name",
    "parent__ghfdb_id",
    "ghfdb_id",
)

EXPECTED_LIST_FILTER = (
    EnvironmentListFilter,
    "parent__corr_HP_flag",
    ChildExplorationMethodListFilter,
    ExplorePurposeListFilter,
    "sample__heatflowinterval__site__country",
    "sample__heatflowinterval__site__region",
    "sample__heatflowinterval__site__continent",
    "sample__heatflowinterval__site__domain",
)


class TestGHFDBAdminChangelist:
    """GHFDBAdmin changelist rendering, search, import page and queryset."""

    @pytest.mark.django_db
    def test_ghfdb_admin_changelist_refined_configuration(self, admin_client, heat_flow_chain):
        """T013: Changelist renders and exposes refined ordered columns/search/filters."""
        from project.ghfdb.resources import (
            GHFDBChildImportResource,
            GHFDBExportResource,
            GHFDBParentImportResource,
        )

        url = reverse("admin:ghfdb_ghfdbchild_changelist")
        response = admin_client.get(url)
        assert response.status_code == 200

        # T079: the tail of list_display is read from constants.py, never
        # restated as a literal here — that restatement is what let three of
        # the published names drift from the canonical definitions (D1, D2).
        headings = [str(header["text"]) for header in result_headers(response.context["cl"])]
        assert headings[-len(CHILD_COLUMNS) :] == list(CHILD_COLUMNS)

        model_admin = admin.site._registry[GHFDBChild]
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
    def test_ghfdb_admin_search_by_name_and_id_parent(self, admin_client, heat_flow_chain):
        """T013: Search works using parent ghfdb_id and site name mapped fields."""
        entry = heat_flow_chain
        entry.parent.ghfdb_id = 99999
        entry.parent.save(update_fields=["ghfdb_id"])

        url = reverse("admin:ghfdb_ghfdbchild_changelist")

        response_by_name = admin_client.get(
            url, {"q": entry.sample.heatflowinterval.site.name}
        )
        assert response_by_name.status_code == 200

        response_by_parent_id = admin_client.get(url, {"q": str(entry.parent.ghfdb_id)})
        assert response_by_parent_id.status_code == 200

    @pytest.mark.django_db
    def test_authenticated_staff_import_page_renders_http200(self, admin_client):
        """T066: Authenticated staff GET /admin/ghfdb/ghfdb/import/ returns HTTP 200.

        Regression for BUG-002: verifies that the django-import-export admin hook
        overrides use request-aware method signatures compatible with v4.x so the
        import page renders without a server error.
        """
        url = reverse("admin:ghfdb_ghfdbchild_import")
        response = admin_client.get(url)
        assert response.status_code == 200, (
            f"Import page returned {response.status_code}; expected 200. Check get_import_resource_classes() signature."
        )

    @pytest.mark.django_db
    def test_ghfdb_admin_queryset_evaluates_without_invalid_prefetch(
        self, admin_user, heat_flow_chain
    ):
        """T080 (BUG-003): Child admin queryset evaluates without invalid prefetch paths."""
        request = RequestFactory().get(reverse("admin:ghfdb_ghfdbchild_changelist"))
        request.user = admin_user

        model_admin = admin.site._registry[GHFDBChild]
        queryset = model_admin.get_queryset(request)

        rows = list(queryset)
        assert rows, "Expected at least one GHFDB child row in queryset evaluation"


class TestGHFDBAdminListFilters:
    """GHFDBAdmin list_filter choices are scoped to their controlled vocabularies."""

    @pytest.mark.django_db
    def test_explo_purpose_filter_choices_are_vocabulary_scoped(
        self, admin_client, heat_flow_chain
    ):
        """T063: explo_purpose list filter choices are restricted to ExplorationPurpose vocabulary.

        Verifies that ExplorePurposeListFilter.lookups() only returns concepts belonging to the
        ExplorationPurpose vocabulary, excluding unrelated generic Concept values.
        """
        from heat_flow.vocabularies import ExplorationPurpose
        from research_vocabs.models import Concept

        model_admin = admin.site._registry[GHFDBChild]

        # Confirm the filter class appears in list_filter (not raw string)
        assert ExplorePurposeListFilter in model_admin.list_filter, (
            "ExplorePurposeListFilter must be present in list_filter"
        )

        # Instantiate filter and collect lookup choices
        f = ExplorePurposeListFilter(
            request=None, params={}, model=GHFDBChild, model_admin=model_admin
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
    def test_environment_filter_choices_are_vocabulary_scoped(self, admin_client):
        """BUG-004: EnvironmentListFilter.lookups() returns GeographicEnvironment vocabulary choices.

        Verifies that the filter shows human-readable vocabulary labels rather than
        raw stored concept keys, and that all returned choices are defined in the
        GeographicEnvironment vocabulary (FR-014, FR-015).
        """
        from heat_flow.vocabularies import GeographicEnvironment

        model_admin = admin.site._registry[GHFDBChild]
        assert EnvironmentListFilter in model_admin.list_filter, (
            "EnvironmentListFilter must be present in list_filter"
        )

        f = EnvironmentListFilter(
            request=None, params={}, model=GHFDBChild, model_admin=model_admin
        )
        lookup_values = {value for value, _label in f.lookups(None, model_admin)}
        vocab_values = {value for value, _label in GeographicEnvironment().choices}

        assert lookup_values, "lookups() must return at least one choice"
        assert lookup_values == vocab_values, (
            f"EnvironmentListFilter choices do not match GeographicEnvironment vocabulary: "
            f"extra={lookup_values - vocab_values}, missing={vocab_values - lookup_values}"
        )

    @pytest.mark.django_db
    def test_explo_method_filter_choices_are_vocabulary_scoped(self, admin_client):
        """BUG-004: ChildExplorationMethodListFilter.lookups() returns ExplorationMethod vocabulary choices.

        Verifies that the filter shows human-readable vocabulary labels rather than
        raw stored concept keys, and that all returned choices are defined in the
        ExplorationMethod vocabulary (FR-014, FR-015).
        """
        from heat_flow.vocabularies import ExplorationMethod

        model_admin = admin.site._registry[GHFDBChild]
        assert ChildExplorationMethodListFilter in model_admin.list_filter, (
            "ChildExplorationMethodListFilter must be present in list_filter"
        )

        f = ChildExplorationMethodListFilter(
            request=None, params={}, model=GHFDBChild, model_admin=model_admin
        )
        lookup_values = {value for value, _label in f.lookups(None, model_admin)}
        vocab_values = {value for value, _label in ExplorationMethod().choices}

        assert lookup_values, "lookups() must return at least one choice"
        assert lookup_values == vocab_values, (
            f"ChildExplorationMethodListFilter choices do not match ExplorationMethod vocabulary: "
            f"extra={lookup_values - vocab_values}, missing={vocab_values - lookup_values}"
        )


class TestGHFDBParentAdminListFilters:
    """GHFDBParentAdmin list_filter choices are scoped to their controlled vocabularies."""

    @pytest.mark.django_db
    def test_parent_environment_filter_choices_are_vocabulary_scoped(self, admin_client):
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
    def test_parent_explo_method_filter_choices_are_vocabulary_scoped(self, admin_client):
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


class TestGHFDBParentAdmin:
    """GHFDBParentAdmin changelist rendering and import resource scoping."""

    @pytest.mark.django_db
    def test_ghfdb_parent_admin_changelist(self, admin_client, heat_flow_chain):
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
    def test_ghfdb_parent_admin_import_resource_only(self, admin_client):
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


# ---------------------------------------------------------------------------
# US-3: the determination changelist (T078-T089).
#
# ``GHFDBChildAdmin``'s columns are built entirely from
# ``project/ghfdb/columns.py``'s published-column mapping (D1, D2), so these
# assert against ``constants.py`` and the rendered page rather than against a
# restated column list.
# ---------------------------------------------------------------------------


class TestGHFDBChildAdmin:
    """The determination changelist: its columns, its scoping, its search and
    filters, and the read-only guarantees around it (US-3)."""

    @pytest.mark.django_db
    def test_changelist_renders_for_a_staff_user(self, staff_client, published_chain):
        """T078 (US-3 acceptance scenario 1)."""
        url = reverse("admin:ghfdb_ghfdbchild_changelist")
        response = staff_client.get(url)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_published_child_columns_appear_in_the_canonical_order(
        self, staff_client, published_chain
    ):
        """T079 (SC-007): the headings Django renders for the tail of
        ``list_display`` equal ``CHILD_COLUMNS``, read from ``constants.py``
        and never from a literal here."""
        url = reverse("admin:ghfdb_ghfdbchild_changelist")
        response = staff_client.get(url)
        headings = [str(header["text"]) for header in result_headers(response.context["cl"])]
        assert headings[-len(CHILD_COLUMNS) :] == list(CHILD_COLUMNS)

    @pytest.mark.django_db
    def test_the_leading_columns_are_the_four_orientation_columns_and_nothing_else(
        self, staff_client, published_chain
    ):
        """T080 (US-3 acceptance scenario 2): the record's published
        identifier, the site's published identifier, the site name and the
        site's two coordinate columns, in that order, and no sixth."""
        url = reverse("admin:ghfdb_ghfdbchild_changelist")
        response = staff_client.get(url)
        cl = response.context["cl"]
        headings = [str(header["text"]) for header in result_headers(cl)]
        # result_headers() prepends an action-checkbox column when the admin
        # offers any bulk action; slice from the offset rather than assuming
        # position 0, so this test does not depend on that unrelated detail.
        offset = len(headings) - len(cl.model_admin.list_display)

        assert headings[offset : offset + 5] == [
            label_for_field("ghfdb_id", GHFDBChild),
            "ID_parent",
            "name",
            "lat_NS",
            "long_EW",
        ]
        assert headings[offset + 5] == CHILD_COLUMNS[0]

    def test_site_values_are_not_restated_on_every_row(self):
        """T081: the intersection of ``list_display`` with the published
        parent columns is exactly the four orientation columns T080 names,
        and nothing further — the familiarity being protected is the child
        block's, per the 2026-08-23 clarification."""
        model_admin = admin.site._registry[GHFDBChild]
        headings = set()
        for item in model_admin.list_display:
            if callable(item):
                headings.add(str(item.short_description))
            else:
                headings.add(str(item))

        assert headings & set(PARENT_COLUMNS) == {"ID_parent", "name", "lat_NS", "long_EW"}

    @pytest.mark.django_db
    def test_search_matches_site_name_and_published_site_identifier(
        self, staff_client, published_chain
    ):
        """T082 (FR-016): exercised through the rendered changelist with a
        query string, not against the search attribute — a search matching
        nothing must return no rows, not just a 200 status."""
        url = reverse("admin:ghfdb_ghfdbchild_changelist")
        site_name = published_chain.sample.heatflowinterval.site.name

        response = staff_client.get(url, {"q": site_name})
        assert response.context["cl"].result_count == 1

        response = staff_client.get(url, {"q": str(published_chain.parent.ghfdb_id)})
        assert response.context["cl"].result_count == 1

        response = staff_client.get(url, {"q": "no-such-site-name-anywhere"})
        assert response.context["cl"].result_count == 0
