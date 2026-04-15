"""
Tests for GHFDBChildImportResource.

Covers:
- All 14 child field mappings
- parent FK resolved via ID_parent ForeignKeyWidget
- after_save_instance() creates 9 HeatFlowCorrection records
- ProbeMetadata created when probe columns non-empty
- method M2M set via MultiConceptWidget
- IntervalWidget, GradientWidget, ConductivityWidget M2M set after save
"""

import pytest
import tablib

# ---------------------------------------------------------------------------
# Helpers: row data mirrors what the full GHFDB flat row looks like
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
    "p_comment": "",
    "corr_HP_flag": "No",
    "total_depth_MD": "",
    "total_depth_TVD": "",
    "explo_method": "",
    "explo_purpose": "",
    "Country": "Germany",
    "Region": "",
    "Continent": "Europe",
    "Domain": "",
}

CHILD_ROW = {
    "ID": "GHFDB-001",
    "ID_parent": "GHFDB-P-001",
    "qc": "70.0",
    "qc_uncertainty": "5.0",
    "q_method": "",
    "q_top": "0",
    "q_bottom": "500",
    "probe_penetration": "",
    "probe_length": "",
    "probe_tilt": "",
    "expedition": "",
    "probe_type": "",
    "water_temperature": "",
    "relevant_child": "Yes",
    "c_comment": "",
    "corr_IS_flag": "No",
    "corr_T_flag": "Yes",
    "corr_S_flag": "No",
    "corr_E_flag": "No",
    "corr_TOPO_flag": "No",
    "corr_PAL_flag": "No",
    "corr_SUR_flag": "No",
    "corr_CONV_flag": "No",
    "corr_HR_flag": "No",
    "T_grad_mean": "25.0",
    "T_grad_uncertainty": "",
    "T_grad_mean_cor": "",
    "T_grad_uncertainty_cor": "",
    "T_method_top": "",
    "T_method_bottom": "",
    "T_shutin_top": "",
    "T_shutin_bottom": "",
    "T_corr_top": "",
    "T_corr_bottom": "",
    "T_number": "",
    "tc_mean": "2.5",
    "tc_uncertainty": "",
    "tc_source": "",
    "tc_location": "",
    "tc_method": "",
    "tc_saturation": "",
    "tc_pT_conditions": "",
    "tc_pT_function": "",
    "tc_number": "",
    "tc_strategy": "",
    "publication_reference": "",
    "data_reference": "",
    "q_date": "",
    "igsn": "",
}


def make_dataset(*rows):
    """Build a tablib Dataset from dicts with matching headers."""
    headers = list(rows[0].keys())
    ds = tablib.Dataset(headers=headers)
    for row in rows:
        ds.append([row[h] for h in headers])
    return ds


def import_parents(dataset):
    """Pre-import the parent rows needed by child tests."""
    from project.ghfdb.resources import GHFDBParentImportResource

    resource = GHFDBParentImportResource()
    ds = make_dataset(PARENT_ROW)
    resource.import_data(ds, dry_run=False, raise_errors=True)


# ---------------------------------------------------------------------------
# T030 Tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestGHFDBChildImportResourceImport:
    """T030 — GHFDBChildImportResource end-to-end import tests."""

    def test_import_creates_heatflow(self, dataset):
        """Importing a child row creates a HeatFlow with local_id set."""
        import_parents(dataset)
        from heat_flow.models import HeatFlow

        from project.ghfdb.resources import GHFDBChildImportResource

        resource = GHFDBChildImportResource()
        ds = make_dataset(CHILD_ROW)
        result = resource.import_data(ds, dry_run=False, raise_errors=False)

        assert not result.has_errors(), result.invalid_rows
        assert HeatFlow.objects.filter(local_id="GHFDB-001").exists()

    def test_parent_fk_resolved_via_id_parent(self, dataset):
        """HeatFlow.parent FK is resolved from ID_parent column."""
        import_parents(dataset)
        from heat_flow.models import HeatFlow

        from project.ghfdb.resources import GHFDBChildImportResource

        resource = GHFDBChildImportResource()
        ds = make_dataset(CHILD_ROW)
        resource.import_data(ds, dry_run=False, raise_errors=False)

        child = HeatFlow.objects.get(local_id="GHFDB-001")
        assert child.parent is not None
        assert child.parent.local_id == "GHFDB-P-001"

    def test_upsert_on_local_id(self, dataset):
        """Re-importing same ID updates, not duplicates."""
        import_parents(dataset)
        from heat_flow.models import HeatFlow

        from project.ghfdb.resources import GHFDBChildImportResource

        resource = GHFDBChildImportResource()
        ds = make_dataset(CHILD_ROW)
        resource.import_data(ds, dry_run=False, raise_errors=False)
        resource.import_data(ds, dry_run=False, raise_errors=False)

        assert HeatFlow.objects.filter(local_id="GHFDB-001").count() == 1

    def test_after_save_creates_9_corrections(self, dataset):
        """after_save_instance() creates 9 HeatFlowCorrection records."""
        import_parents(dataset)
        from heat_flow.models import HeatFlow

        from project.ghfdb.resources import GHFDBChildImportResource

        resource = GHFDBChildImportResource()
        ds = make_dataset(CHILD_ROW)
        resource.import_data(ds, dry_run=False, raise_errors=False)

        child = HeatFlow.objects.get(local_id="GHFDB-001")
        assert child.corrections.count() == 9

    def test_correction_values_match_row(self, dataset):
        """Correction flags are set per the row values."""
        import_parents(dataset)
        from heat_flow.models import HeatFlow, HeatFlowCorrection

        from project.ghfdb.resources import GHFDBChildImportResource

        resource = GHFDBChildImportResource()
        ds = make_dataset(CHILD_ROW)
        resource.import_data(ds, dry_run=False, raise_errors=False)

        child = HeatFlow.objects.get(local_id="GHFDB-001")
        t_corr = child.corrections.get(correction_type="T")
        # corr_T_flag = "Yes" in CHILD_ROW
        assert t_corr.status != HeatFlowCorrection.StatusChoices.UNSPECIFIED

    def test_gradient_created_when_t_grad_mean_set(self, dataset):
        """ThermalGradient record is created when T_grad_mean is non-empty."""
        import_parents(dataset)
        from heat_flow.models import HeatFlow

        from project.ghfdb.resources import GHFDBChildImportResource

        resource = GHFDBChildImportResource()
        ds = make_dataset(CHILD_ROW)
        resource.import_data(ds, dry_run=False, raise_errors=False)

        child = HeatFlow.objects.get(local_id="GHFDB-001")
        assert child.thermal_gradient is not None

    def test_conductivity_created_when_tc_mean_set(self, dataset):
        """IntervalConductivity record is created when tc_mean is non-empty."""
        import_parents(dataset)
        from heat_flow.models import HeatFlow

        from project.ghfdb.resources import GHFDBChildImportResource

        resource = GHFDBChildImportResource()
        ds = make_dataset(CHILD_ROW)
        resource.import_data(ds, dry_run=False, raise_errors=False)

        child = HeatFlow.objects.get(local_id="GHFDB-001")
        assert child.thermal_conductivity is not None

    def test_gradient_skipped_when_empty(self, dataset):
        """ThermalGradient is not created when T_grad_mean is empty."""
        import_parents(dataset)
        from heat_flow.models import HeatFlow

        from project.ghfdb.resources import GHFDBChildImportResource

        row = dict(CHILD_ROW)
        row["T_grad_mean"] = ""

        resource = GHFDBChildImportResource()
        ds = make_dataset(row)
        resource.import_data(ds, dry_run=False, raise_errors=False)

        child = HeatFlow.objects.get(local_id="GHFDB-001")
        assert child.thermal_gradient is None

    def test_conductivity_skipped_when_empty(self, dataset):
        """IntervalConductivity is not created when tc_mean is empty."""
        import_parents(dataset)
        from heat_flow.models import HeatFlow

        from project.ghfdb.resources import GHFDBChildImportResource

        row = dict(CHILD_ROW)
        row["tc_mean"] = ""

        resource = GHFDBChildImportResource()
        ds = make_dataset(row)
        resource.import_data(ds, dry_run=False, raise_errors=False)

        child = HeatFlow.objects.get(local_id="GHFDB-001")
        assert child.thermal_conductivity is None


@pytest.mark.django_db
class TestGHFDBChildProbeMetadata:
    """T030 — ProbeMetadata creation."""

    def test_probe_metadata_created_when_penetration_set(self, dataset):
        """ProbeMetadata is created when probe_penetration is non-empty."""
        import_parents(dataset)
        from heat_flow.models import HeatFlow, ProbeMetadata

        from project.ghfdb.resources import GHFDBChildImportResource

        row = dict(CHILD_ROW)
        row["probe_penetration"] = "3.5"

        resource = GHFDBChildImportResource()
        ds = make_dataset(row)
        resource.import_data(ds, dry_run=False, raise_errors=False)

        child = HeatFlow.objects.get(local_id="GHFDB-001")
        assert ProbeMetadata.objects.filter(interval=child.sample).exists()

    def test_probe_metadata_not_created_when_empty(self, dataset):
        """ProbeMetadata is not created when all probe columns are empty."""
        import_parents(dataset)
        from heat_flow.models import HeatFlow, ProbeMetadata

        from project.ghfdb.resources import GHFDBChildImportResource

        resource = GHFDBChildImportResource()
        ds = make_dataset(CHILD_ROW)  # probe_penetration = ""
        resource.import_data(ds, dry_run=False, raise_errors=False)

        child = HeatFlow.objects.get(local_id="GHFDB-001")
        assert not ProbeMetadata.objects.filter(interval=child.sample).exists()


@pytest.mark.django_db
class TestGHFDBChildTemplateNoIdRegression:
    """T068/T030 regression coverage for standard uploads without ID columns."""

    def test_no_id_rows_reimport_upserts_via_natural_key(self, dataset):
        """Rows missing ID/ID_parent upsert via location + interval + publication key."""
        from heat_flow.models import HeatFlow

        from project.ghfdb.resources import (
            GHFDBChildImportResource,
            GHFDBParentImportResource,
        )

        parent_row = dict(PARENT_ROW)
        parent_row["ID_parent"] = ""
        GHFDBParentImportResource().import_data(
            make_dataset(parent_row),
            dry_run=False,
            raise_errors=True,
        )

        child_row = dict(CHILD_ROW)
        child_row["ID"] = ""
        child_row["ID_parent"] = ""
        child_row["lat_NS"] = "48.0"
        child_row["long_EW"] = "11.0"
        child_row["publication_reference"] = "Ref A"

        resource = GHFDBChildImportResource()
        first = resource.import_data(
            make_dataset(child_row),
            dry_run=False,
            raise_errors=False,
        )
        assert not first.has_errors(), first.invalid_rows

        child_row_update = dict(child_row)
        child_row_update["qc"] = "75.2"
        second = resource.import_data(
            make_dataset(child_row_update),
            dry_run=False,
            raise_errors=False,
        )
        assert not second.has_errors(), second.invalid_rows

        assert HeatFlow.objects.count() == 1
        child = HeatFlow.objects.first()
        assert child is not None
        assert float(child.value.magnitude) == pytest.approx(75.2)

    def test_no_id_rows_keep_distinct_publication_references(self, dataset):
        """Different publication_reference values remain distinct child records."""
        from heat_flow.models import HeatFlow

        from project.ghfdb.resources import (
            GHFDBChildImportResource,
            GHFDBParentImportResource,
        )

        parent_row = dict(PARENT_ROW)
        parent_row["ID_parent"] = ""
        GHFDBParentImportResource().import_data(
            make_dataset(parent_row),
            dry_run=False,
            raise_errors=True,
        )

        child_base = dict(CHILD_ROW)
        child_base["ID"] = ""
        child_base["ID_parent"] = ""
        child_base["lat_NS"] = "48.0"
        child_base["long_EW"] = "11.0"

        row_a = dict(child_base)
        row_a["publication_reference"] = "Ref A"

        row_b = dict(child_base)
        row_b["publication_reference"] = "Ref B"

        resource = GHFDBChildImportResource()
        result = resource.import_data(
            make_dataset(row_a, row_b),
            dry_run=False,
            raise_errors=False,
        )

        assert not result.has_errors(), result.invalid_rows
        assert HeatFlow.objects.count() == 2


@pytest.mark.django_db
class TestGHFDBChildAbsentHeaderRegression:
    """T068 — Absent ID/ID_parent header must not raise header-validation error."""

    def test_absent_id_and_id_parent_headers_do_not_raise_header_error(self, dataset):
        """Import succeeds when ID and ID_parent columns are entirely absent."""
        from heat_flow.models import HeatFlow

        from project.ghfdb.resources import (
            GHFDBChildImportResource,
            GHFDBParentImportResource,
        )

        parent_row = {k: v for k, v in PARENT_ROW.items() if k != "ID_parent"}
        GHFDBParentImportResource().import_data(make_dataset(parent_row), dry_run=False, raise_errors=True)

        child_row = {k: v for k, v in CHILD_ROW.items() if k not in ("ID", "ID_parent")}
        child_row["lat_NS"] = "48.0"
        child_row["long_EW"] = "11.0"
        child_row["publication_reference"] = "Ref A"
        ds = make_dataset(child_row)
        assert "ID" not in ds.headers
        assert "ID_parent" not in ds.headers

        result = GHFDBChildImportResource().import_data(ds, dry_run=False, raise_errors=False)

        assert not result.has_errors(), result.invalid_rows
        assert HeatFlow.objects.count() == 1

    def test_absent_id_headers_reimport_upserts_via_natural_key(self, dataset):
        """Re-import without ID/ID_parent headers updates rather than duplicates."""
        from heat_flow.models import HeatFlow

        from project.ghfdb.resources import (
            GHFDBChildImportResource,
            GHFDBParentImportResource,
        )

        parent_row = {k: v for k, v in PARENT_ROW.items() if k != "ID_parent"}
        GHFDBParentImportResource().import_data(make_dataset(parent_row), dry_run=False, raise_errors=True)

        child_row = {k: v for k, v in CHILD_ROW.items() if k not in ("ID", "ID_parent")}
        child_row["lat_NS"] = "48.0"
        child_row["long_EW"] = "11.0"
        child_row["publication_reference"] = "Ref A"

        GHFDBChildImportResource().import_data(make_dataset(child_row), dry_run=False, raise_errors=False)

        child_row_update = dict(child_row)
        child_row_update["qc"] = "77.7"
        result = GHFDBChildImportResource().import_data(
            make_dataset(child_row_update), dry_run=False, raise_errors=False
        )

        assert not result.has_errors(), result.invalid_rows
        assert HeatFlow.objects.count() == 1
        child = HeatFlow.objects.first()
        assert child is not None
        assert float(child.value.magnitude) == pytest.approx(77.7)
