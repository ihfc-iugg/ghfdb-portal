# Tests for GHFDB admin changelist configuration and rendering (FS-002).

import pytest
from django.contrib import admin
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
    @pytest.mark.django_db
    def test_ghfdb_admin_changelist_refined_configuration(
        self, admin_client, heat_flow_chain
    ):
        from project.ghfdb.resources import (
            GHFDBChildImportResource,
            GHFDBExportResource,
            GHFDBParentImportResource,
        )

        url = reverse("admin:ghfdb_ghfdbchild_changelist")
        response = admin_client.get(url)
        assert response.status_code == 200

        # The tail of list_display is read from constants.py, never
        # restated as a literal here — that restatement is what let three of
        # the published names drift from the canonical definitions (FS-002).
        headings = [
            str(header["text"]) for header in result_headers(response.context["cl"])
        ]
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

    @pytest.mark.django_db
    def test_authenticated_staff_import_page_renders_http200(self, admin_client):
        # Authenticated staff GET /admin/ghfdb/ghfdb/import/ returns HTTP 200.
        url = reverse("admin:ghfdb_ghfdbchild_import")
        response = admin_client.get(url)
        assert response.status_code == 200, (
            f"Import page returned {response.status_code}; expected 200. Check get_import_resource_classes() signature."
        )

    @pytest.mark.django_db
    def test_ghfdb_admin_queryset_evaluates_without_invalid_prefetch(
        self, admin_user, heat_flow_chain
    ):
        request = RequestFactory().get(reverse("admin:ghfdb_ghfdbchild_changelist"))
        request.user = admin_user

        model_admin = admin.site._registry[GHFDBChild]
        queryset = model_admin.get_queryset(request)

        rows = list(queryset)
        assert rows, "Expected at least one GHFDB child row in queryset evaluation"


class TestGHFDBAdminListFilters:
    @pytest.mark.django_db
    def test_explo_purpose_filter_choices_are_vocabulary_scoped(
        self, admin_client, heat_flow_chain
    ):
        # explo_purpose list filter choices are restricted to ExplorationPurpose
        # vocabulary.
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
        # EnvironmentListFilter.lookups() returns GeographicEnvironment vocabulary
        # choices.
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
        # ChildExplorationMethodListFilter.lookups() returns ExplorationMethod
        # vocabulary choices.
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
    @pytest.mark.django_db
    def test_parent_environment_filter_choices_are_vocabulary_scoped(
        self, admin_client
    ):
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


# GHFDBParent admin tests


class TestGHFDBParentAdmin:
    # The site changelist: its columns, its scoping, its search and filters, and the
    # read-only guarantees around it (US-3).

    @pytest.mark.django_db
    def test_ghfdb_parent_admin_changelist(self, admin_client, heat_flow_chain):
        url = reverse("admin:ghfdb_ghfdbparent_changelist")
        response = admin_client.get(url)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_ghfdb_parent_admin_import_resource_only(self, admin_client):
        # FS-002 US-1b: GHFDBParentAdmin.get_import_resource_classes() returns only
        # GHFDBParentImportResource — no child or export resource attached.
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

    def test_process_dataset_delegates_to_the_shared_entry_point(self, monkeypatch):
        # The commit step calls ``import_ghfdb_template()`` rather than re-implementing
        # the parent-then-child sequence here.
        import tablib

        from project.ghfdb.models import GHFDBParent

        called = {}

        def fake_import_ghfdb_template(file, dataset):
            called["file"] = file
            called["dataset"] = dataset
            return "OUTCOME-SENTINEL"

        monkeypatch.setattr(
            "project.ghfdb.importers.import_ghfdb_template",
            fake_import_ghfdb_template,
        )

        model_admin = admin.site._registry[GHFDBParent]
        ds = tablib.Dataset(headers=["name"])
        request = RequestFactory().get("/")

        result = model_admin.process_dataset(ds, form=None, request=request)

        assert result == "OUTCOME-SENTINEL"
        assert called["file"] is ds
        assert called["dataset"] is None  # no dataset-selection surface yet (FS-004)

    @pytest.mark.django_db
    def test_changelist_renders_for_a_staff_user(self, staff_client, published_chain):
        url = reverse("admin:ghfdb_ghfdbparent_changelist")
        response = staff_client.get(url)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_published_parent_columns_appear_in_the_canonical_order(
        self, staff_client, published_chain
    ):
        # FS-002 SC-007: the rendered headings, read from ``PARENT_COLUMNS``, asserted
        # the same way as for the determination changelist.
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
        # Country, region, continent and geological domain, in that order,
        # immediately after the published columns.
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
        # the two determination-count columns render last, and render their values.
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
        # FS-002 FR-016: exercised through the rendered changelist with a query string,
        # not against the search attribute — a search matching nothing must return no
        # rows, not just a 200 status.
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
        # FS-002 FR-017: environment, heat production correction flag, exploration
        # method, exploration purpose, country, region, continent and geological domain,
        # each producing matching rows when applied.
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
        # FS-002 FR-018, SC-009: SC-009 requires this proven on both changelists, not
        # once.
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
        # FS-002 FR-012, SC-008: as the determination changelist's equivalent test, with
        # the same note about the import route — a separate surface.
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
        url = reverse("admin:ghfdb_ghfdbparent_changelist")
        response = staff_client.get(url)
        result_list = list(response.context["cl"].result_list)
        assert published_chain.parent in result_list
        assert unpublished_chain.parent not in result_list

    @pytest.mark.django_db
    def test_published_columns_and_geography_render_real_values(
        self, staff_client, published_chain
    ):
        # F5 : as the determination changelist's equivalent test, but also covering the
        # geography block — a heading assertion cannot tell ``get_country`` resolving
        # from it silently returning ``None``.
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
        # FS-002 FR-019, SC-003, measured on the rendered changelist.
        url = reverse("admin:ghfdb_ghfdbparent_changelist")

        def call():
            staff_client.get(url)

        with override_settings(ORBIT={"ENABLED": False}):
            call()
            constant_query_count(published_chains, call)

    def test_every_declared_path_resolves_on_the_model(self):
        # FS-002 FR-020: Django's own admin checks report nothing for this
        # registration, covering the display, filter and search declarations together.
        from django.contrib.admin.checks import ModelAdminChecks

        from project.ghfdb.models import GHFDBParent

        model_admin = admin.site._registry[GHFDBParent]
        errors = ModelAdminChecks().check(model_admin)
        assert errors == []

    def test_it_carries_the_site_import_resource_and_no_export_resource(self):
        # FS-002 FR-021, SC-010. The negative half is as much of the requirement as the
        # positive.
        from project.ghfdb.models import GHFDBParent
        from project.ghfdb.resources import GHFDBParentImportResource

        model_admin = admin.site._registry[GHFDBParent]
        assert model_admin.get_import_resource_classes(request=None) == [
            GHFDBParentImportResource
        ]
        assert model_admin.get_export_resource_classes(request=None) == []


class TestGHFDBChildAdmin:
    # The determination changelist: its columns, its scoping, its search and filters,
    # and the read-only guarantees around it (US-3).

    @pytest.mark.django_db
    def test_changelist_renders_for_a_staff_user(self, staff_client, published_chain):
        url = reverse("admin:ghfdb_ghfdbchild_changelist")
        response = staff_client.get(url)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_published_child_columns_appear_in_the_canonical_order(
        self, staff_client, published_chain
    ):
        # FS-002 SC-007: the headings Django renders for the tail of ``list_display``
        # equal ``CHILD_COLUMNS``, read from ``constants.py`` and never from a literal
        # here.
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
        # FS-002 US-3 acceptance scenario 2: the record's published identifier, the
        # site's published identifier, the site name and the site's two coordinate
        # columns, in that order, and no sixth.
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
        # The intersection of ``list_display`` with the published parent columns is
        # exactly the four orientation columns FS-002 names, and nothing further — the
        # familiarity being protected is the child block's, per the 2026-08-23
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
        # FS-002 FR-016: exercised through the rendered changelist with a query string,
        # not against the search attribute — a search matching nothing must return no
        # rows, not just a 200 status.
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
        # FS-002 FR-017: environment, heat production correction flag, exploration
        # method, exploration purpose, country, region, continent and geological domain,
        # each producing matching rows when applied.
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
        # FS-002 FR-018, SC-009: every term of its own vocabulary is offered, no term of
        # another vocabulary is, and the choice text is the label rather than the stored
        # key.
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
        # FS-002 FR-012, SC-008: the three permission hooks refuse, and the rendered
        # page carries no add link and no per-row change link. The import route is a
        # separate surface, out of this dispatch's scope.
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
        # FS-002 FR-002, SC-005: the assertion FS-002 R6 records as catching an
        # override that stopped going through the scoped manager.
        url = reverse("admin:ghfdb_ghfdbchild_changelist")
        response = staff_client.get(url)
        result_list = list(response.context["cl"].result_list)
        assert published_chain in result_list
        assert unpublished_chain not in result_list

    @pytest.mark.django_db
    def test_published_columns_render_real_values_not_only_headings(
        self, staff_client, published_chain
    ):
        # F5 : a heading assertion cannot tell a working column from a blank one — every
        # column assertion elsewhere in this module reads a heading.
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
        # FS-002 FR-019, SC-003, US-3 acceptance scenario 8, measured on the rendered
        # changelist.
        url = reverse("admin:ghfdb_ghfdbchild_changelist")

        def call():
            staff_client.get(url)

        with override_settings(ORBIT={"ENABLED": False}):
            call()
            constant_query_count(published_chains, call)

    def test_every_declared_path_resolves_on_the_model(self):
        # FS-002 FR-020: Django's own admin checks report nothing for this
        # registration, covering the display, filter and search declarations together.
        from django.contrib.admin.checks import ModelAdminChecks

        model_admin = admin.site._registry[GHFDBChild]
        errors = ModelAdminChecks().check(model_admin)
        assert errors == []

    def test_it_carries_the_determination_import_resource_and_the_export_resource(self):
        from project.ghfdb.resources import (
            GHFDBChildImportResource,
            GHFDBExportResource,
        )

        model_admin = admin.site._registry[GHFDBChild]
        assert model_admin.get_import_resource_classes(request=None) == [
            GHFDBChildImportResource
        ]
        assert model_admin.get_export_resource_classes(request=None) == [
            GHFDBExportResource
        ]


class TestResourceAttachment:
    # FS-002 FR-021, SC-010: the negative half of the export requirement proven across
    # both changelists at once — no resource, import or export, is attached to both.

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
    # FS-002 FR-012: ``django-import-export`` grants the import route to any staff user
    # while ``IMPORT_EXPORT_IMPORT_PERMISSION_CODE`` is unset — verified unset in this
    # project — so both registrations, which declare no add, no change and no delete.

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
