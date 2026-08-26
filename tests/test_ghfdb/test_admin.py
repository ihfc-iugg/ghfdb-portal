"""Tests for GHFDB admin changelist configuration and rendering (T013, T063,
T066, T078-T089, T098-T110, T123)."""

import pathlib

import pytest
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.admin.templatetags.admin_list import result_headers
from django.contrib.admin.utils import label_for_field
from django.test import RequestFactory, override_settings
from django.urls import reverse

from project.ghfdb.admin import (
    ChildExplorationMethodListFilter,
    EnvironmentListFilter,
    ExplorePurposeListFilter,
    ParentEnvironmentListFilter,
    ParentExplorationMethodListFilter,
    ParentExplorePurposeListFilter,
)
from project.ghfdb.columns import ColumnDisplay
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
    def test_ghfdb_admin_changelist_refined_configuration(
        self, admin_client, heat_flow_chain
    ):
        """T013: Changelist renders and exposes refined ordered columns/search/filters."""
        from project.ghfdb.resources import (
            GHFDBChildImportResource,
            GHFDBExportResource,
            GHFDBParentImportResource,
            GHFDBReleaseImportResource,
        )

        url = reverse("admin:ghfdb_ghfdbchild_changelist")
        response = admin_client.get(url)
        assert response.status_code == 200

        # T079: the tail of list_display is read from constants.py, never
        # restated as a literal here — that restatement is what let three of
        # the published names drift from the canonical definitions (D1, D2).
        headings = [
            str(header["text"]) for header in result_headers(response.context["cl"])
        ]
        assert headings[-len(CHILD_COLUMNS) :] == list(CHILD_COLUMNS)

        model_admin = admin.site._registry[GHFDBChild]
        assert model_admin.search_fields == EXPECTED_SEARCH_FIELDS
        assert model_admin.list_filter == EXPECTED_LIST_FILTER
        # D21: the release resource joins the determination changelist's
        # import machinery once US-1's all-or-nothing guarantee is
        # registered (T030) - grown here from a single-resource state,
        # not restated as a literal independent of that registration.
        assert model_admin.get_import_resource_classes(request=None) == [
            GHFDBChildImportResource,
            GHFDBReleaseImportResource,
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
    def test_parent_environment_filter_choices_are_vocabulary_scoped(
        self, admin_client
    ):
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
    def test_parent_explo_method_filter_choices_are_vocabulary_scoped(
        self, admin_client
    ):
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


class TestGHFDBParentAdmin:
    """The site changelist: its columns, its scoping, its search and
    filters, and the read-only guarantees around it (US-3). Column-order
    assertions read ``PARENT_COLUMNS`` from ``constants.py`` rather than a
    restated literal (D1) — the two module-level literals this class used to
    compare ``list_display`` and its headers against are gone; T099 is what
    replaces them."""

    @pytest.mark.django_db
    def test_ghfdb_parent_admin_changelist(self, admin_client, heat_flow_chain):
        """Renders, and carries the model's verbose name. Column order and
        heading assertions are T099-T101, below."""
        url = reverse("admin:ghfdb_ghfdbparent_changelist")
        response = admin_client.get(url)
        assert response.status_code == 200

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

    @pytest.mark.django_db
    def test_changelist_renders_for_a_staff_user(self, staff_client, published_chain):
        """T098 (US-3 acceptance scenario 3)."""
        url = reverse("admin:ghfdb_ghfdbparent_changelist")
        response = staff_client.get(url)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_published_parent_columns_appear_in_the_canonical_order(
        self, staff_client, published_chain
    ):
        """T099 (SC-007): the rendered headings, read from ``PARENT_COLUMNS``,
        asserted as T079 asserts them for the determination changelist."""
        from project.ghfdb.models import GHFDBParent

        url = reverse("admin:ghfdb_ghfdbparent_changelist")
        response = staff_client.get(url)
        cl = response.context["cl"]
        headings = [str(header["text"]) for header in result_headers(cl)]
        offset = len(headings) - len(admin.site._registry[GHFDBParent].list_display)

        assert headings[offset : offset + len(PARENT_COLUMNS)] == list(PARENT_COLUMNS)

    @pytest.mark.django_db
    def test_the_geography_follows_the_published_block(
        self, staff_client, published_chain
    ):
        """T100 (D8): country, region, continent and geological domain, in
        that order, immediately after the published columns."""
        from project.ghfdb.models import GHFDBParent

        url = reverse("admin:ghfdb_ghfdbparent_changelist")
        response = staff_client.get(url)
        cl = response.context["cl"]
        headings = [str(header["text"]) for header in result_headers(cl)]
        offset = len(headings) - len(admin.site._registry[GHFDBParent].list_display)
        start = offset + len(PARENT_COLUMNS)

        assert headings[start : start + 4] == [
            "country",
            "region",
            "continent",
            "domain",
        ]

    @pytest.mark.django_db
    def test_the_two_determination_counts_come_last(
        self, staff_client, published_chain
    ):
        """T101: the two determination-count columns render last, and
        render their values."""
        url = reverse("admin:ghfdb_ghfdbparent_changelist")
        response = staff_client.get(url)
        cl = response.context["cl"]
        headings = [str(header["text"]) for header in result_headers(cl)]
        assert headings[-2:] == ["total_children", "relevant_children"]

        row = next(iter(cl.result_list))
        assert row.total_children == 1
        assert row.relevant_children == 0

    @pytest.mark.django_db
    def test_search_matches_site_name_and_published_site_identifier(
        self, staff_client, published_chain
    ):
        """T102 (FR-016): exercised through the rendered changelist with a
        query string, not against the search attribute — a search matching
        nothing must return no rows, not just a 200 status."""
        url = reverse("admin:ghfdb_ghfdbparent_changelist")
        parent = published_chain.parent
        site_name = parent.sample.name

        response = staff_client.get(url, {"q": site_name})
        assert response.context["cl"].result_count == 1

        response = staff_client.get(url, {"q": str(parent.ghfdb_id)})
        assert response.context["cl"].result_count == 1

        response = staff_client.get(url, {"q": "no-such-site-name-anywhere"})
        assert response.context["cl"].result_count == 0

    @pytest.mark.django_db
    def test_the_eight_filters_are_offered(self, staff_client, published_chain):
        """T103 (FR-017): environment, heat production correction flag,
        exploration method, exploration purpose, country, region, continent
        and geological domain, each producing matching rows when applied."""
        from heat_flow.vocabularies import ExplorationMethod, ExplorationPurpose
        from research_vocabs.models import Concept

        from project.ghfdb.models import GHFDBParent

        model_admin = admin.site._registry[GHFDBParent]
        assert len(model_admin.list_filter) == 8

        parent = published_chain.parent
        site = parent.sample
        explo_method_value = ExplorationMethod().choices[0][0]
        purpose = Concept.get_for_vocabulary(ExplorationPurpose).first()
        site.explo_method = explo_method_value
        site.region = "Bavaria"
        site.domain = "Continental"
        site.save()
        site.explo_purpose.set([purpose])
        parent.corr_HP_flag = True
        parent.save()

        url = reverse("admin:ghfdb_ghfdbparent_changelist")
        filters = {
            "environment": str(site.environment),
            "corr_HP_flag__exact": "1",
            "explo_method": explo_method_value,
            "explo_purpose": purpose.pk,
            "sample__heatflowsite__country": site.country,
            "sample__heatflowsite__region": site.region,
            "sample__heatflowsite__continent": site.continent,
            "sample__heatflowsite__domain": site.domain,
        }
        for param, value in filters.items():
            response = staff_client.get(url, {param: value})
            assert response.context["cl"].result_count == 1, param

    @pytest.mark.django_db
    def test_each_vocabulary_filter_offers_exactly_its_own_terms_as_labels(self):
        """T104 (FR-018, SC-009): SC-009 requires this proven on both
        changelists, not once."""
        from heat_flow.vocabularies import (
            ExplorationMethod,
            ExplorationPurpose,
            GeographicEnvironment,
        )
        from research_vocabs.models import Concept

        from project.ghfdb.models import GHFDBParent

        model_admin = admin.site._registry[GHFDBParent]

        environment_filter = ParentEnvironmentListFilter(
            request=None, params={}, model=GHFDBParent, model_admin=model_admin
        )
        assert dict(environment_filter.lookups(None, model_admin)) == dict(
            GeographicEnvironment().choices
        )

        method_filter = ParentExplorationMethodListFilter(
            request=None, params={}, model=GHFDBParent, model_admin=model_admin
        )
        assert dict(method_filter.lookups(None, model_admin)) == dict(
            ExplorationMethod().choices
        )

        purpose_filter = ParentExplorePurposeListFilter(
            request=None, params={}, model=GHFDBParent, model_admin=model_admin
        )
        purpose_choices = dict(purpose_filter.lookups(None, model_admin))
        expected_purposes = {
            concept.pk: concept.label
            for concept in Concept.get_for_vocabulary(ExplorationPurpose)
        }
        assert purpose_choices == expected_purposes

    @pytest.mark.django_db
    def test_there_is_no_route_to_add_change_or_delete(
        self, staff_client, published_chain
    ):
        """T105 (FR-012, SC-008): as T085, with the same note about the
        import route — a separate surface, covered by T123."""
        from project.ghfdb.models import GHFDBParent

        model_admin = admin.site._registry[GHFDBParent]
        request = RequestFactory().get("/")
        assert model_admin.has_add_permission(request) is False
        assert model_admin.has_change_permission(request) is False
        assert model_admin.has_delete_permission(request) is False

        url = reverse("admin:ghfdb_ghfdbparent_changelist")
        response = staff_client.get(url)
        content = response.content.decode()

        assert reverse("admin:ghfdb_ghfdbparent_add") not in content
        change_url = reverse(
            "admin:ghfdb_ghfdbparent_change", args=[published_chain.parent.pk]
        )
        assert change_url not in content

    @pytest.mark.django_db
    def test_an_unpublished_site_is_absent_from_the_rendered_rows(
        self, staff_client, published_chain, unpublished_chain
    ):
        """T106 (FR-002, SC-005)."""
        url = reverse("admin:ghfdb_ghfdbparent_changelist")
        response = staff_client.get(url)
        result_list = list(response.context["cl"].result_list)
        assert published_chain.parent in result_list
        assert unpublished_chain.parent not in result_list

    @pytest.mark.django_db
    def test_published_columns_and_geography_render_real_values(
        self, staff_client, published_chain
    ):
        """F5 (D14): as the determination changelist's equivalent test, but
        also covering the geography block (D15) — a heading assertion
        cannot tell ``get_country`` resolving from it silently returning
        ``None``."""
        from heat_flow.vocabularies import ExplorationPurpose
        from research_vocabs.models import Concept

        from project.ghfdb.models import GHFDBParent

        site = published_chain.parent.sample
        site.country = "Wonderland"
        site.save(update_fields=["country"])
        purpose = Concept.get_for_vocabulary(ExplorationPurpose).first()
        site.explo_purpose.set([purpose])
        published_chain.parent.corr_HP_flag = True
        published_chain.parent.save(update_fields=["corr_HP_flag"])

        url = reverse("admin:ghfdb_ghfdbparent_changelist")
        response = staff_client.get(url)
        row = next(iter(response.context["cl"].result_list))
        model_admin = admin.site._registry[GHFDBParent]

        # annotation column, read through the exact callable list_display
        # renders — not the raw row attribute.
        q_rendered = ColumnDisplay.build("q")(row)
        assert (
            getattr(q_rendered, "magnitude", q_rendered) == published_chain.parent.value
        )
        # field column
        assert ColumnDisplay.build("corr_HP_flag")(row) is True
        # many-valued column
        assert ColumnDisplay.build("explo_purpose")(row) == str(purpose)
        # geography column, read through the bound admin method itself
        assert model_admin.get_country(row) == "Wonderland"

    @pytest.mark.django_db
    def test_query_count_is_equal_at_two_row_counts(
        self, staff_client, published_chains, constant_query_count
    ):
        """T107 (FR-019, SC-003), measured on the rendered changelist.

        Follows D12: the framework's ``orbit`` audit-log watcher costs
        roughly three queries per rendered row, which is not this
        changelist's own cost, so it is disabled for the duration of the
        comparison, exactly as the determination changelist's equivalent
        test disables it — see that test's docstring for the measurement.
        """
        url = reverse("admin:ghfdb_ghfdbparent_changelist")

        def call():
            staff_client.get(url)

        with override_settings(ORBIT={"ENABLED": False}):
            call()
            constant_query_count(published_chains, call)

    def test_every_declared_path_resolves_on_the_model(self):
        """T108 (FR-020): Django's own admin checks report nothing for this
        registration, covering the display, filter and search declarations
        together."""
        from django.contrib.admin.checks import ModelAdminChecks

        from project.ghfdb.models import GHFDBParent

        model_admin = admin.site._registry[GHFDBParent]
        errors = ModelAdminChecks().check(model_admin)
        assert errors == []

    def test_it_carries_the_site_import_resource_and_no_export_resource(self):
        """T109 (FR-021, SC-010). The negative half is as much of the
        requirement as the positive."""
        from project.ghfdb.models import GHFDBParent
        from project.ghfdb.resources import GHFDBParentImportResource

        model_admin = admin.site._registry[GHFDBParent]
        assert model_admin.get_import_resource_classes(request=None) == [
            GHFDBParentImportResource
        ]
        assert model_admin.get_export_resource_classes(request=None) == []


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
        headings = [
            str(header["text"]) for header in result_headers(response.context["cl"])
        ]
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

        assert headings & set(PARENT_COLUMNS) == {
            "ID_parent",
            "name",
            "lat_NS",
            "long_EW",
        }

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

    @pytest.mark.django_db
    def test_the_eight_filters_are_offered(self, staff_client, published_chain):
        """T083 (FR-017): environment, heat production correction flag,
        exploration method, exploration purpose, country, region, continent
        and geological domain, each producing matching rows when applied."""
        from heat_flow.vocabularies import ExplorationMethod, ExplorationPurpose
        from research_vocabs.models import Concept

        model_admin = admin.site._registry[GHFDBChild]
        assert len(model_admin.list_filter) == 8

        site = published_chain.sample.heatflowinterval.site
        explo_method_value = ExplorationMethod().choices[0][0]
        purpose = Concept.get_for_vocabulary(ExplorationPurpose).first()
        site.explo_method = explo_method_value
        site.region = "Bavaria"
        site.domain = "Continental"
        site.save()
        site.explo_purpose.set([purpose])
        published_chain.parent.corr_HP_flag = True
        published_chain.parent.save()

        url = reverse("admin:ghfdb_ghfdbchild_changelist")
        filters = {
            "environment": str(site.environment),
            "parent__corr_HP_flag__exact": "1",
            "explo_method": explo_method_value,
            "explo_purpose": purpose.pk,
            "sample__heatflowinterval__site__country": site.country,
            "sample__heatflowinterval__site__region": site.region,
            "sample__heatflowinterval__site__continent": site.continent,
            "sample__heatflowinterval__site__domain": site.domain,
        }
        for param, value in filters.items():
            response = staff_client.get(url, {param: value})
            assert response.context["cl"].result_count == 1, param

    @pytest.mark.django_db
    def test_each_vocabulary_filter_offers_exactly_its_own_terms_as_labels(self):
        """T084 (FR-018, SC-009): every term of its own vocabulary is
        offered, no term of another vocabulary is, and the choice text is the
        label rather than the stored key."""
        from heat_flow.vocabularies import (
            ExplorationMethod,
            ExplorationPurpose,
            GeographicEnvironment,
        )
        from research_vocabs.models import Concept

        model_admin = admin.site._registry[GHFDBChild]

        environment_filter = EnvironmentListFilter(
            request=None, params={}, model=GHFDBChild, model_admin=model_admin
        )
        assert dict(environment_filter.lookups(None, model_admin)) == dict(
            GeographicEnvironment().choices
        )

        method_filter = ChildExplorationMethodListFilter(
            request=None, params={}, model=GHFDBChild, model_admin=model_admin
        )
        assert dict(method_filter.lookups(None, model_admin)) == dict(
            ExplorationMethod().choices
        )

        purpose_filter = ExplorePurposeListFilter(
            request=None, params={}, model=GHFDBChild, model_admin=model_admin
        )
        purpose_choices = dict(purpose_filter.lookups(None, model_admin))
        expected_purposes = {
            concept.pk: concept.label
            for concept in Concept.get_for_vocabulary(ExplorationPurpose)
        }
        assert purpose_choices == expected_purposes

    @pytest.mark.django_db
    def test_there_is_no_route_to_add_change_or_delete(
        self, staff_client, published_chain
    ):
        """T085 (FR-012, SC-008): the three permission hooks refuse, and the
        rendered page carries no add link and no per-row change link. The
        import route is a separate surface, covered by T123, out of this
        dispatch's scope."""
        model_admin = admin.site._registry[GHFDBChild]
        request = RequestFactory().get("/")
        assert model_admin.has_add_permission(request) is False
        assert model_admin.has_change_permission(request) is False
        assert model_admin.has_delete_permission(request) is False

        url = reverse("admin:ghfdb_ghfdbchild_changelist")
        response = staff_client.get(url)
        content = response.content.decode()

        assert reverse("admin:ghfdb_ghfdbchild_add") not in content
        change_url = reverse("admin:ghfdb_ghfdbchild_change", args=[published_chain.pk])
        assert change_url not in content

    @pytest.mark.django_db
    def test_an_unpublished_determination_is_absent_from_the_rendered_rows(
        self, staff_client, published_chain, unpublished_chain
    ):
        """T086 (FR-002, SC-005): the assertion R6 records as catching an
        override that stopped going through the scoped manager."""
        url = reverse("admin:ghfdb_ghfdbchild_changelist")
        response = staff_client.get(url)
        result_list = list(response.context["cl"].result_list)
        assert published_chain in result_list
        assert unpublished_chain not in result_list

    @pytest.mark.django_db
    def test_published_columns_render_real_values_not_only_headings(
        self, staff_client, published_chain
    ):
        """F5 (D14): a heading assertion cannot tell a working column from a
        blank one — every column assertion elsewhere in this module reads a
        heading. This reads real values off a rendered row and compares them
        to what the fixture stored: one annotation column, one field column
        and one many-valued column."""
        from heat_flow.vocabularies import HeatFlowMethod
        from research_vocabs.models import Concept

        method = Concept.get_for_vocabulary(HeatFlowMethod).first()
        published_chain.method.set([method])
        published_chain.expedition = "R/V Test Expedition"
        published_chain.save(update_fields=["expedition"])

        url = reverse("admin:ghfdb_ghfdbchild_changelist")
        response = staff_client.get(url)
        row = next(iter(response.context["cl"].result_list))

        # annotation column, read through the exact callable list_display
        # renders — not the raw row attribute, which would pass even if the
        # callable itself were broken.
        qc_rendered = ColumnDisplay.build("qc")(row)
        assert getattr(qc_rendered, "magnitude", qc_rendered) == published_chain.value
        # field column
        assert ColumnDisplay.build("expedition")(row) == "R/V Test Expedition"
        # many-valued column
        assert ColumnDisplay.build("q_method")(row) == str(method)

    @pytest.mark.django_db
    def test_query_count_is_equal_at_two_row_counts(
        self, staff_client, published_chains, constant_query_count
    ):
        """T087 (FR-019, SC-003; US-3 acceptance scenario 8), measured on the
        rendered changelist.

        ``fairdm``'s ``orbit`` app installs a global audit-log watcher
        (unrelated to this admin, on every project built on the framework)
        that inserts a row per signal it observes, so a raw query count
        across a full request is not a measurement of this changelist alone.
        Disabled for the duration of the comparison, which is the standard,
        live-checked way to quiet it (``orbit.conf.get_config()`` reads
        ``settings.ORBIT`` on every record, not only at startup). One warm-up
        request is also taken first, because the very first request in a test
        pays a one-off framework singleton-creation cost that the second
        request does not — without it, low and high never compare like for
        like regardless of row count.
        """
        url = reverse("admin:ghfdb_ghfdbchild_changelist")

        def call():
            staff_client.get(url)

        with override_settings(ORBIT={"ENABLED": False}):
            call()
            constant_query_count(published_chains, call)

    def test_every_declared_path_resolves_on_the_model(self):
        """T088 (FR-020): Django's own admin checks report nothing for this
        registration, covering the display, filter and search declarations
        together."""
        from django.contrib.admin.checks import ModelAdminChecks

        model_admin = admin.site._registry[GHFDBChild]
        errors = ModelAdminChecks().check(model_admin)
        assert errors == []

    def test_it_carries_the_determination_import_resource_and_the_export_resource(self):
        """T089 (FR-021, SC-010): both the import and the export attachment.

        D21: grown to include the release resource once US-1's
        all-or-nothing guarantee is registered (T030) - the export side
        is untouched, since the release story adds no export resource.
        """
        from project.ghfdb.resources import (
            GHFDBChildImportResource,
            GHFDBExportResource,
            GHFDBReleaseImportResource,
        )

        model_admin = admin.site._registry[GHFDBChild]
        assert model_admin.get_import_resource_classes(request=None) == [
            GHFDBChildImportResource,
            GHFDBReleaseImportResource,
        ]
        assert model_admin.get_export_resource_classes(request=None) == [
            GHFDBExportResource
        ]


class TestResourceAttachment:
    """T110 (FR-021, SC-010): the negative half of the export requirement
    proven across both changelists at once — no resource, import or export,
    is attached to both."""

    def test_no_resource_is_attached_to_both_changelists(self):
        from project.ghfdb.models import GHFDBParent

        child_admin = admin.site._registry[GHFDBChild]
        parent_admin = admin.site._registry[GHFDBParent]

        child_import = set(child_admin.get_import_resource_classes(request=None))
        parent_import = set(parent_admin.get_import_resource_classes(request=None))
        assert not (child_import & parent_import)

        child_export = set(child_admin.get_export_resource_classes(request=None))
        parent_export = set(parent_admin.get_export_resource_classes(request=None))
        assert not (child_export & parent_export)
        assert parent_export == set()


class TestImportPermission:
    """T123 (FR-012): ``django-import-export`` grants the import route to
    any staff user while ``IMPORT_EXPORT_IMPORT_PERMISSION_CODE`` is unset —
    verified unset in this project — so both registrations, which declare no
    add, no change and no delete, otherwise carry a route that writes
    records and that a user holding only view permission can reach. Gated on
    both registrations behind the model's add permission at the user
    level."""

    @pytest.mark.django_db
    def test_view_only_staff_is_refused_the_determination_import_page(
        self, staff_client
    ):
        url = reverse("admin:ghfdb_ghfdbchild_import")
        response = staff_client.get(url)
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_staff_holding_add_permission_reaches_the_determination_import_page(
        self, client, db
    ):
        from django.contrib.auth import get_user_model
        from django.contrib.auth.models import Permission

        user = get_user_model().objects.create_user(
            email="ghfdb-child-importer@example.com",
            password="ghfdb-child-importer-password",
            is_staff=True,
        )
        permissions = Permission.objects.filter(
            content_type__app_label="ghfdb",
            codename__in=["view_ghfdbchild", "add_ghfdbchild"],
        )
        user.user_permissions.set(permissions)
        client.force_login(user)

        url = reverse("admin:ghfdb_ghfdbchild_import")
        response = client.get(url)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_view_only_staff_is_refused_the_site_import_page(self, staff_client):
        url = reverse("admin:ghfdb_ghfdbparent_import")
        response = staff_client.get(url)
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_staff_holding_add_permission_reaches_the_site_import_page(
        self, client, db
    ):
        from django.contrib.auth import get_user_model
        from django.contrib.auth.models import Permission

        user = get_user_model().objects.create_user(
            email="ghfdb-parent-importer@example.com",
            password="ghfdb-parent-importer-password",
            is_staff=True,
        )
        permissions = Permission.objects.filter(
            content_type__app_label="ghfdb",
            codename__in=["view_ghfdbparent", "add_ghfdbparent"],
        )
        user.user_permissions.set(permissions)
        client.force_login(user)

        url = reverse("admin:ghfdb_ghfdbparent_import")
        response = client.get(url)
        assert response.status_code == 200


class TestAnonymousRequestToTheImportRoute:
    """T033: an anonymous request to the import route is refused,
    distinguishably from a request that merely redirects to a login page
    for any administrative address. Every unauthenticated request to any
    admin URL redirects to the login page the same way, so a test that
    only checks for a redirect would pass even if this route carried no
    permission check of its own. ``has_import_permission`` is exercised
    directly, the same mechanism T031's staff-without-permission case
    already relies on, to prove the refusal is the route's own and not
    merely the generic authentication wall in front of it."""

    def test_anonymous_get_redirects_to_login_for_this_route(self, client):
        url = reverse("admin:ghfdb_ghfdbchild_import")
        response = client.get(url)

        assert response.status_code == 302
        assert response.url == f"/admin/login/?next={url}"

    def test_has_import_permission_itself_refuses_an_anonymous_user(self):
        from django.contrib.auth.models import AnonymousUser

        model_admin = admin.site._registry[GHFDBChild]
        request = RequestFactory().get(reverse("admin:ghfdb_ghfdbchild_import"))
        request.user = AnonymousUser()

        assert model_admin.has_import_permission(request) is False


def _release_dataset(mutate=None):
    """A tablib ``Dataset`` built from the real release base fixture (the
    same one ``test_release.py`` uses), header-corrected for the two
    published misspellings (D7) - the file a curator would submit, not
    the archive as downloaded. ``mutate`` receives the header and the
    list-of-lists rows and may change them in place before the dataset is
    built, so a scenario can carry exactly one refused value or one
    repeated identifier without hand-building a whole valid row."""
    import csv
    from pathlib import Path

    import tablib

    from project.ghfdb.constants import MISSPELLED_COLUMNS

    fixture = (
        Path(__file__).parent
        / "test_resources"
        / "fixtures"
        / "release"
        / "release_sample.csv"
    )
    text = fixture.read_text(encoding="utf-8-sig")
    reader = csv.reader(text.splitlines())
    header = [MISSPELLED_COLUMNS.get(name, name) for name in next(reader)]
    rows = [list(row) for row in reader]
    if mutate:
        mutate(header, rows)
    dataset = tablib.Dataset(headers=header)
    for row in rows:
        dataset.append(row)
    return dataset


class _StubConfirmForm:
    """A minimal stand-in for ``ConfirmImportForm``, carrying only the
    ``cleaned_data`` keys ``process_dataset`` itself reads - the resource
    index (so the release resource, not the child one, is chosen) and the
    original file name."""

    def __init__(self, resource_index):
        self.cleaned_data = {
            "resource": str(resource_index),
            "original_file_name": "release.csv",
        }


def _release_resource_index(admin_instance):
    from project.ghfdb.resources import GHFDBReleaseImportResource

    return admin_instance.get_import_resource_classes(request=None).index(
        GHFDBReleaseImportResource
    )


def _confirmed_import(admin_instance, dataset, user):
    """Run ``dataset`` through the exact method a curator's confirm click
    invokes (``ImportMixin.process_import`` calls this directly), so the
    result carries what ``process_result`` needs (T028, T029) - built
    with a real request instead of a mock, per craft-tdd."""
    request = RequestFactory().post(reverse("admin:ghfdb_ghfdbchild_import"))
    request.user = user
    request.session = {}
    form = _StubConfirmForm(_release_resource_index(admin_instance))
    result = admin_instance.process_dataset(dataset, form, request)
    return result, request


def _refuse_one_row(header, rows):
    """Give the first data row an unrecognised lithology term (T081,
    T082's own established way to produce a refused value) - a purely
    per-row refusal, unlike a ``SITE_COLUMNS``/``PROBE_COLUMNS`` entry,
    which would also fail every other row sharing that row's site or
    interval as a disagreement. Leaves every other row untouched and
    valid."""
    rows[0][header.index("geo_lithology")] = "not_a_real_lithology"


class TestGHFDBChildAdminAllOrNothingImport:
    """T025-T030 (D9, D21): the confirmed pass on the determination
    changelist writes nothing at all when any value in the file is
    refused, and never reports such an import as having succeeded. The
    release resource is what makes this reachable (T030) - the same
    override, registered once on this changelist, also reaches the
    contributor template's reader (plan.md, 'Where it is registered')."""

    @pytest.mark.django_db
    def test_a_refused_value_writes_nothing_at_all(self):
        """T025: every record count is exactly what it was before,
        including for the rows that were themselves valid. Fails before:
        the library's default commits the valid rows and skips the
        refused one."""
        from fairdm.core.models import Dataset
        from heat_flow.models import HeatFlow, HeatFlowSite, ParentHeatFlow
        from literature.models import LiteratureItem

        from project.ghfdb.admin import GHFDBChildAdmin
        from project.ghfdb.resources import GHFDBReleaseImportResource

        dataset = _release_dataset(mutate=_refuse_one_row)
        admin_instance = GHFDBChildAdmin(GHFDBChild, AdminSite())
        imp_kwargs = admin_instance.get_import_data_kwargs()

        result = GHFDBReleaseImportResource().import_data(
            dataset, dry_run=False, raise_errors=False, **imp_kwargs
        )

        assert result.has_validation_errors() is True
        assert HeatFlow.objects.count() == 0
        assert HeatFlowSite.objects.count() == 0
        assert ParentHeatFlow.objects.count() == 0
        assert Dataset.all_objects.count() == 0
        assert LiteratureItem.objects.count() == 0

    @pytest.mark.django_db
    def test_reinstating_the_librarys_default_makes_the_guarantee_fail(self):
        """T027: reinstating ``rollback_on_validation_errors=False`` (the
        library's own default, which
        ``GHFDBChildAdmin.get_import_data_kwargs`` overrides) on the
        exact scenario T025 proves lets the valid rows commit and skips
        only the refused one - proving the override is what T025 depends
        on, not incidental behaviour of a clean file."""
        from heat_flow.models import HeatFlow

        from project.ghfdb.resources import GHFDBReleaseImportResource

        dataset = _release_dataset(mutate=_refuse_one_row)
        total_rows = len(dataset)

        result = GHFDBReleaseImportResource().import_data(
            dataset, dry_run=False, raise_errors=False
        )

        assert result.has_validation_errors() is True
        assert HeatFlow.objects.count() == total_rows - 1

    @pytest.mark.django_db
    def test_a_refused_import_is_not_reported_as_succeeded(self, admin_user):
        """T028, T029: the confirmed pass's result is checked before
        anything is reported as done. Fails before: ``process_result``
        reports success without inspecting the result it was given."""
        from django.contrib import messages as messages_module
        from django.contrib.messages.storage.fallback import FallbackStorage

        from project.ghfdb.admin import GHFDBChildAdmin

        dataset = _release_dataset(mutate=_refuse_one_row)
        admin_instance = GHFDBChildAdmin(GHFDBChild, AdminSite())
        result, request = _confirmed_import(admin_instance, dataset, admin_user)
        assert result.has_validation_errors() is True
        request._messages = FallbackStorage(request)

        admin_instance.process_result(result, request)

        levels = {message.level for message in request._messages}
        assert messages_module.SUCCESS not in levels
        assert messages_module.ERROR in levels

    @pytest.mark.django_db
    def test_a_clean_file_is_still_reported_as_succeeded(self, admin_user):
        """The other branch of T028/T029's check: a clean import is
        unaffected and still reports success, proving the check is real
        rather than always refusing."""
        from django.contrib import messages as messages_module
        from django.contrib.messages.storage.fallback import FallbackStorage

        from project.ghfdb.admin import GHFDBChildAdmin

        dataset = _release_dataset()
        admin_instance = GHFDBChildAdmin(GHFDBChild, AdminSite())
        result, request = _confirmed_import(admin_instance, dataset, admin_user)
        assert result.has_validation_errors() is False
        request._messages = FallbackStorage(request)

        admin_instance.process_result(result, request)

        levels = {message.level for message in request._messages}
        assert messages_module.SUCCESS in levels
        assert messages_module.ERROR not in levels

    @pytest.mark.django_db
    def test_a_clean_file_writes_its_records_once_registered(self):
        """T030: the release format and resource are registered on the
        determination changelist, and a file in which every value passes
        writes the records when the curator confirms. Fails before: no
        reader is registered here at all."""
        from heat_flow.models import HeatFlow

        from project.ghfdb.admin import GHFDBChildAdmin
        from project.ghfdb.resources import GHFDBReleaseImportResource

        admin_instance = GHFDBChildAdmin(GHFDBChild, AdminSite())
        assert GHFDBReleaseImportResource in admin_instance.get_import_resource_classes(
            request=None
        )

        dataset = _release_dataset()
        imp_kwargs = admin_instance.get_import_data_kwargs()

        result = GHFDBReleaseImportResource().import_data(
            dataset, dry_run=False, raise_errors=False, **imp_kwargs
        )

        assert result.has_validation_errors() is False
        assert HeatFlow.objects.count() == len(dataset)


DOCS_DIR = pathlib.Path(__file__).resolve().parents[2] / "docs"
IMPORTING_DATA_GUIDE = DOCS_DIR / "guides" / "importing-data.md"


class TestImportingDataGuide:
    """T110: a curator with a published release file can find what the
    portal reads, where the import is, what a refusal reports and how to
    act on it, and what happens to a file that fails - reached from the
    documentation's own contents, not merely present on disk."""

    def test_the_page_exists_and_is_reachable_from_the_contents(self):
        assert IMPORTING_DATA_GUIDE.exists()
        index = (DOCS_DIR / "index.md").read_text()
        assert "guides/importing-data" in index

    def test_it_covers_what_a_curator_needs(self):
        """Read from the page itself, not assumed from the file existing,
        per this task's own acceptance: the four things a curator needs
        are all present."""
        page = IMPORTING_DATA_GUIDE.read_text()
        assert "GHFDB Release Format" in page  # the file it reads, named as the curator sees it
        assert "Import" in page  # where the import is
        assert "refused" in page  # what a refusal reports
        assert "Nothing is written" in page  # what happens when a file fails
