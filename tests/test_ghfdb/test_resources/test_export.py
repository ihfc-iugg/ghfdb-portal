"""
Tests for GHFDBExportResource.

T041 — User Story 3

Covers:
- Column set matches all 62 GHFDB_COLUMN_ORDER entries
- Column order is identical to GHFDB_COLUMN_ORDER
- Pint quantity fields render as plain numeric magnitude (no unit symbol)
- M2M fields render as semicolon-separated labels
- get_queryset() returns GHFDB.objects.for_export()
- Filtered queryset exports only matching records
- Staff-only access (anonymous admin export URL → 302)
"""

import pytest

from project.ghfdb.resources._base import GHFDB_COLUMN_ORDER

# ---------------------------------------------------------------------------
# T041: Resource class structure tests
# ---------------------------------------------------------------------------


class TestGHFDBExportResourceDeclaration:
    """GHFDBExportResource declares exactly the 62 GHFDB columns."""

    def test_all_62_columns_declared(self):
        """GHFDBExportResource has a Field for each of the 62 GHFDB_COLUMN_ORDER entries."""
        from project.ghfdb.resources.export import GHFDBExportResource

        resource = GHFDBExportResource()
        field_names = set(resource.fields.keys())
        missing = set(GHFDB_COLUMN_ORDER) - field_names
        assert not missing, f"Missing fields: {missing}"

    def test_no_extra_columns_beyond_column_order(self):
        """No fields beyond GHFDB_COLUMN_ORDER are declared."""
        from project.ghfdb.resources.export import GHFDBExportResource

        resource = GHFDBExportResource()
        field_names = set(resource.fields.keys())
        extra = field_names - set(GHFDB_COLUMN_ORDER)
        assert not extra, f"Extra undocumented fields: {extra}"

    def test_export_order_matches_ghfdb_column_order(self):
        """Meta.export_order must equal GHFDB_COLUMN_ORDER exactly."""
        from project.ghfdb.resources.export import GHFDBExportResource

        assert tuple(GHFDBExportResource.Meta.export_order) == GHFDB_COLUMN_ORDER


# ---------------------------------------------------------------------------
# T041: Queryset tests
# ---------------------------------------------------------------------------


class TestGHFDBExportQueryset:
    """get_queryset() returns a GHFDB.objects.for_export() queryset."""

    @pytest.mark.django_db
    def test_get_queryset_returns_ghfdb_querytype(self):
        """get_queryset() returns a GHFDBQuerySet."""
        from project.ghfdb.managers import GHFDBQuerySet
        from project.ghfdb.resources.export import GHFDBExportResource

        resource = GHFDBExportResource()
        qs = resource.get_queryset()
        assert isinstance(qs, GHFDBQuerySet)

    @pytest.mark.django_db
    def test_filtered_queryset_exports_only_matching_records(self, heat_flow_chain):
        """A filtered queryset exports only the matching records."""
        from project.ghfdb.models import GHFDB
        from project.ghfdb.resources.export import GHFDBExportResource

        resource = GHFDBExportResource()
        qs = GHFDB.objects.for_export().filter(pk=heat_flow_chain.pk)
        dataset = resource.export(qs)
        assert len(dataset) == 1

    @pytest.mark.django_db
    def test_empty_queryset_exports_headers_only(self):
        """An empty queryset exports headers but no data rows."""
        from project.ghfdb.models import GHFDB
        from project.ghfdb.resources.export import GHFDBExportResource

        resource = GHFDBExportResource()
        qs = GHFDB.objects.none()
        dataset = resource.export(qs)
        assert len(dataset) == 0
        assert list(dataset.headers) == list(GHFDB_COLUMN_ORDER)


# ---------------------------------------------------------------------------
# T041: Column order tests
# ---------------------------------------------------------------------------


class TestGHFDBExportColumnOrder:
    """Exported headers appear in GHFDB_COLUMN_ORDER sequence."""

    @pytest.mark.django_db
    def test_exported_headers_match_column_order(self, heat_flow_chain):
        """Exported dataset column headers appear in exact GHFDB_COLUMN_ORDER sequence."""
        from project.ghfdb.models import GHFDB
        from project.ghfdb.resources.export import GHFDBExportResource

        resource = GHFDBExportResource()
        qs = GHFDB.objects.for_export().filter(pk=heat_flow_chain.pk)
        dataset = resource.export(qs)
        assert list(dataset.headers) == list(GHFDB_COLUMN_ORDER)


# ---------------------------------------------------------------------------
# T041: Pint quantity rendering tests
# ---------------------------------------------------------------------------


class TestGHFDBExportQuantityFields:
    """Pint quantity fields render as plain numeric magnitudes."""

    @pytest.mark.django_db
    def test_qc_renders_as_plain_number(self, heat_flow_chain):
        """Exported 'qc' value is a plain number (no Pint Quantity object)."""
        from project.ghfdb.models import GHFDB
        from project.ghfdb.resources.export import GHFDBExportResource

        resource = GHFDBExportResource()
        qs = GHFDB.objects.for_export().filter(pk=heat_flow_chain.pk)
        dataset = resource.export(qs)
        row = dataset.dict[0]
        qc_val = row["qc"]
        assert not hasattr(qc_val, "magnitude"), f"Expected plain number, got Quantity: {qc_val!r}"
        assert qc_val is not None and str(qc_val) != ""

    @pytest.mark.django_db
    def test_t_grad_mean_renders_as_plain_number(self, heat_flow_chain):
        """Exported 't_grad_mean' value is a plain number."""
        from project.ghfdb.models import GHFDB
        from project.ghfdb.resources.export import GHFDBExportResource

        resource = GHFDBExportResource()
        qs = GHFDB.objects.for_export().filter(pk=heat_flow_chain.pk)
        dataset = resource.export(qs)
        row = dataset.dict[0]
        grad_val = row["t_grad_mean"]
        assert not hasattr(grad_val, "magnitude"), f"Expected plain number, got Quantity: {grad_val!r}"
        assert grad_val is not None and str(grad_val) != ""

    @pytest.mark.django_db
    def test_tc_mean_renders_as_plain_number(self, heat_flow_chain):
        """Exported 'tc_mean' value is a plain number."""
        from project.ghfdb.models import GHFDB
        from project.ghfdb.resources.export import GHFDBExportResource

        resource = GHFDBExportResource()
        qs = GHFDB.objects.for_export().filter(pk=heat_flow_chain.pk)
        dataset = resource.export(qs)
        row = dataset.dict[0]
        tc_val = row["tc_mean"]
        assert not hasattr(tc_val, "magnitude"), f"Expected plain number, got Quantity: {tc_val!r}"
        assert tc_val is not None and str(tc_val) != ""


# ---------------------------------------------------------------------------
# T041: M2M rendering tests
# ---------------------------------------------------------------------------


class TestGHFDBExportM2MFields:
    """M2M fields render as semicolon-separated label strings."""

    @pytest.mark.django_db
    def test_empty_q_method_renders_as_empty_string(self, heat_flow_chain):
        """Exported 'q_method' renders as '' when no methods are set."""
        from project.ghfdb.models import GHFDB
        from project.ghfdb.resources.export import GHFDBExportResource

        resource = GHFDBExportResource()
        qs = GHFDB.objects.for_export().filter(pk=heat_flow_chain.pk)
        dataset = resource.export(qs)
        row = dataset.dict[0]
        assert row["q_method"] in ("", None)

    @pytest.mark.django_db
    def test_empty_t_method_top_renders_as_empty_string(self, heat_flow_chain):
        """Exported 't_method_top' renders as '' when no methods are set."""
        from project.ghfdb.models import GHFDB
        from project.ghfdb.resources.export import GHFDBExportResource

        resource = GHFDBExportResource()
        qs = GHFDB.objects.for_export().filter(pk=heat_flow_chain.pk)
        dataset = resource.export(qs)
        row = dataset.dict[0]
        assert row["t_method_top"] in ("", None)


# ---------------------------------------------------------------------------
# T041: Staff-only access control
# ---------------------------------------------------------------------------


class TestGHFDBExportAccessControl:
    """Export admin URL requires staff authentication."""

    @pytest.mark.django_db
    def test_anonymous_admin_export_url_redirects(self, client):
        """Anonymous GET to the GHFDB admin export URL returns a 302 redirect."""
        from django.urls import reverse

        url = reverse("admin:ghfdb_ghfdb_export")
        response = client.get(url)
        assert response.status_code == 302
