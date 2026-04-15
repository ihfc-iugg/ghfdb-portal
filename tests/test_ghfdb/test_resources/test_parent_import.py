"""
Tests for GHFDBParentImportResource.

Covers:
- Upsert on local_id (re-import updates, does not duplicate)
- before_import() deduplication keeps first occurrence of each ID_parent
- 18 parent columns mapped to correct fields
- ParentHeatFlow.sample FK (to HeatFlowSite) created with correct Point location
- explo_purpose M2M set
- Staff-only access control (anonymous admin import URL -> 302)
"""

import pytest
import tablib
from django.contrib.auth import get_user_model

User = get_user_model()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PARENT_ROW = {
    "ID_parent": "GHFDB-P-001",
    "q": "70.0",
    "q_uncertainty": "5.0",
    "name": "Test Site Alpha",
    "lat_NS": "48.0",
    "long_EW": "11.0",
    "elevation": "500",
    "environment": "Onshore (continental)",
    "p_comment": "test comment",
    "corr_HP_flag": "No",
    "total_depth_MD": "1000",
    "total_depth_TVD": "900",
    "explo_method": "",
    "explo_purpose": "Hydrocarbon",
    "Country": "Germany",
    "Region": "Bavaria",
    "Continent": "Europe",
    "Domain": "",
}


def make_dataset(*rows):
    """Build a tablib Dataset from dicts with matching headers."""
    headers = list(rows[0].keys())
    ds = tablib.Dataset(headers=headers)
    for row in rows:
        ds.append([row[h] for h in headers])
    return ds


# ---------------------------------------------------------------------------
# T029 Tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestGHFDBParentImportResourceImport:
    """T029 — GHFDBParentImportResource end-to-end import tests."""

    def test_import_creates_parent_and_site(self, dataset):
        """Importing a row creates one ParentHeatFlow and one HeatFlowSite."""
        from heat_flow.models import HeatFlowSite, ParentHeatFlow

        from project.ghfdb.resources import GHFDBParentImportResource

        resource = GHFDBParentImportResource()
        ds = make_dataset(PARENT_ROW)
        result = resource.import_data(ds, dry_run=False, raise_errors=False)

        assert not result.has_errors(), result.invalid_rows
        assert ParentHeatFlow.objects.filter(local_id="GHFDB-P-001").exists()
        assert HeatFlowSite.objects.filter(name="Test Site Alpha").exists()

    def test_upsert_on_local_id_does_not_duplicate(self, dataset):
        """Re-importing the same ID_parent updates, does not create a second record."""
        from heat_flow.models import ParentHeatFlow

        from project.ghfdb.resources import GHFDBParentImportResource

        resource = GHFDBParentImportResource()
        ds = make_dataset(PARENT_ROW)
        resource.import_data(ds, dry_run=False, raise_errors=False)
        resource.import_data(ds, dry_run=False, raise_errors=False)

        assert ParentHeatFlow.objects.filter(local_id="GHFDB-P-001").count() == 1

    def test_upsert_updates_existing_record(self, dataset):
        """Re-importing with changed q value updates the existing ParentHeatFlow."""
        from heat_flow.models import ParentHeatFlow

        from project.ghfdb.resources import GHFDBParentImportResource

        resource = GHFDBParentImportResource()
        ds1 = make_dataset(PARENT_ROW)
        resource.import_data(ds1, dry_run=False, raise_errors=False)

        updated = dict(PARENT_ROW)
        updated["q"] = "80.0"
        ds2 = make_dataset(updated)
        resource.import_data(ds2, dry_run=False, raise_errors=False)

        parent = ParentHeatFlow.objects.get(local_id="GHFDB-P-001")
        assert float(parent.value.magnitude) == pytest.approx(80.0)

    def test_site_has_correct_point_location(self, dataset):
        """Imported HeatFlowSite has a Point at (long_EW, lat_NS)."""
        from heat_flow.models import HeatFlowSite

        from project.ghfdb.resources import GHFDBParentImportResource

        resource = GHFDBParentImportResource()
        ds = make_dataset(PARENT_ROW)
        resource.import_data(ds, dry_run=False, raise_errors=False)

        site = HeatFlowSite.objects.get(name="Test Site Alpha")
        assert site.location is not None
        assert float(site.location.x) == pytest.approx(11.0)
        assert float(site.location.y) == pytest.approx(48.0)

    def test_explo_purpose_m2m_set(self, dataset):
        """Imported HeatFlowSite has explo_purpose M2M populated."""
        from heat_flow.models import HeatFlowSite

        from project.ghfdb.resources import GHFDBParentImportResource

        resource = GHFDBParentImportResource()
        ds = make_dataset(PARENT_ROW)
        resource.import_data(ds, dry_run=False, raise_errors=False)

        site = HeatFlowSite.objects.get(name="Test Site Alpha")
        assert site.explo_purpose.count() >= 1

    def test_all_18_parent_columns_accepted(self, dataset):
        """Resource accepts all 18 PARENT_COLUMNS without field errors."""
        from project.ghfdb.resources import GHFDBParentImportResource

        resource = GHFDBParentImportResource()
        ds = make_dataset(PARENT_ROW)
        result = resource.import_data(ds, dry_run=True, raise_errors=False)
        assert not result.has_errors(), result.invalid_rows


@pytest.mark.django_db
class TestGHFDBParentBeforeImportDedup:
    """T029 — before_import() deduplication."""

    def test_dedup_keeps_first_row_per_id_parent(self, dataset):
        """before_import() keeps only the first row for each ID_parent."""
        from heat_flow.models import ParentHeatFlow

        from project.ghfdb.resources import GHFDBParentImportResource

        resource = GHFDBParentImportResource()
        row1 = dict(PARENT_ROW)
        row2 = dict(PARENT_ROW)
        row2["q"] = "99.9"  # different value but same ID_parent

        ds = make_dataset(row1, row2)
        resource.import_data(ds, dry_run=False, raise_errors=False)

        assert ParentHeatFlow.objects.filter(local_id="GHFDB-P-001").count() == 1
        parent = ParentHeatFlow.objects.get(local_id="GHFDB-P-001")
        # First row's value should be used
        assert float(parent.value.magnitude) == pytest.approx(70.0)


@pytest.mark.django_db
class TestGHFDBParentTemplateNoIdRegression:
    """T067/T029 regression coverage for template uploads without ID_parent."""

    def test_no_id_parent_dedup_uses_lat_long_natural_key(self, dataset):
        """Rows without ID_parent deduplicate by lat_NS + long_EW."""
        from heat_flow.models import HeatFlowSite, ParentHeatFlow

        from project.ghfdb.resources import GHFDBParentImportResource

        row1 = dict(PARENT_ROW)
        row1["ID_parent"] = ""
        row2 = dict(PARENT_ROW)
        row2["ID_parent"] = ""
        row2["q"] = "99.9"  # would overwrite only if second row were imported

        resource = GHFDBParentImportResource()
        ds = make_dataset(row1, row2)
        result = resource.import_data(ds, dry_run=False, raise_errors=False)

        assert not result.has_errors(), result.invalid_rows
        assert ParentHeatFlow.objects.count() == 1
        assert HeatFlowSite.objects.count() == 1
        parent = ParentHeatFlow.objects.first()
        assert parent is not None
        assert float(parent.value.magnitude) == pytest.approx(70.0)

    def test_absent_id_parent_header_does_not_raise_header_error(self, dataset):
        """Import succeeds when ID_parent column is entirely absent from headers."""
        from heat_flow.models import HeatFlowSite, ParentHeatFlow

        from project.ghfdb.resources import GHFDBParentImportResource

        row = {k: v for k, v in PARENT_ROW.items() if k != "ID_parent"}
        ds = make_dataset(row)
        assert "ID_parent" not in ds.headers

        result = GHFDBParentImportResource().import_data(ds, dry_run=False, raise_errors=False)

        assert not result.has_errors(), result.invalid_rows
        assert ParentHeatFlow.objects.count() == 1
        assert HeatFlowSite.objects.count() == 1

    def test_absent_id_parent_header_reimport_upserts(self, dataset):
        """Re-import without ID_parent header updates records rather than duplicating."""
        from heat_flow.models import ParentHeatFlow

        from project.ghfdb.resources import GHFDBParentImportResource

        row = {k: v for k, v in PARENT_ROW.items() if k != "ID_parent"}
        GHFDBParentImportResource().import_data(make_dataset(row), dry_run=False, raise_errors=False)

        row_update = dict(row)
        row_update["q"] = "88.8"
        result = GHFDBParentImportResource().import_data(make_dataset(row_update), dry_run=False, raise_errors=False)

        assert not result.has_errors(), result.invalid_rows
        assert ParentHeatFlow.objects.count() == 1
        parent = ParentHeatFlow.objects.first()
        assert parent is not None
        assert float(parent.value.magnitude) == pytest.approx(88.8)

    def test_no_id_parent_reimport_updates_existing_parent(self, dataset):
        """Re-import without ID_parent upserts via lat_NS + long_EW key."""
        from heat_flow.models import ParentHeatFlow

        from project.ghfdb.resources import GHFDBParentImportResource

        resource = GHFDBParentImportResource()
        row = dict(PARENT_ROW)
        row["ID_parent"] = ""

        resource.import_data(make_dataset(row), dry_run=False, raise_errors=False)

        row_update = dict(row)
        row_update["q"] = "81.5"
        result = resource.import_data(
            make_dataset(row_update),
            dry_run=False,
            raise_errors=False,
        )

        assert not result.has_errors(), result.invalid_rows
        assert ParentHeatFlow.objects.count() == 1
        parent = ParentHeatFlow.objects.first()
        assert parent is not None
        assert float(parent.value.magnitude) == pytest.approx(81.5)


class TestGHFDBParentImportResourceAccessControl:
    """T029 — Staff-only access control."""

    def test_anonymous_admin_import_url_redirects(self, client):
        """Anonymous access to admin import URL redirects (302)."""
        from django.urls import reverse

        url = reverse("admin:ghfdb_ghfdb_import")
        response = client.get(url)
        assert response.status_code == 302
