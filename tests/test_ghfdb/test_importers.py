"""
Tests for project.ghfdb.importers.

Covers:
- import_ghfdb_template() runs the parent pass then the child pass against
  the dataset the caller names, from either raw XLSX bytes or an
  already-parsed tablib.Dataset.
"""

import pytest
import tablib

ROW = {
    "ID_parent": "1",
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
    "ID": "1",
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
    "corr_T_flag": "No",
    "corr_S_flag": "No",
    "corr_E_flag": "No",
    "corr_TOPO_flag": "No",
    "corr_PAL_flag": "No",
    "corr_SUR_flag": "No",
    "corr_CONV_flag": "No",
    "corr_HR_flag": "No",
    "T_grad_mean": "",
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
    "tc_mean": "",
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


def _build_official_xlsx(headers: list, data_rows: list[list]) -> bytes:
    """Build an in-memory XLSX with the official GHFDB layout: header on row
    6, unit/range rows on 7-8 (left blank here), data from row 9 —
    the layout ``GHFDBImportFormat`` (used internally by the entry point)
    reads."""
    from io import BytesIO

    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "data list"

    for i in range(1, 6):
        ws.cell(row=i, column=1, value=f"Metadata row {i}")

    for col_idx, header in enumerate(headers, start=1):
        ws.cell(row=6, column=col_idx, value=header)

    for row_idx, row_values in enumerate(data_rows, start=9):
        for col_idx, value in enumerate(row_values, start=1):
            ws.cell(row=row_idx, column=col_idx, value=value)

    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


@pytest.mark.django_db
class TestImportGHFDBTemplate:
    """T013 — one callable, taking a file and a dataset, running both
    resources in the right order inside one transaction."""

    def test_runs_parent_then_child_pass_from_raw_file_bytes(self, dataset):
        """A raw XLSX file produces both the site+parent and the
        determination beneath it, both attached to the named dataset."""
        from heat_flow.models import HeatFlow, HeatFlowSite, ParentHeatFlow

        from project.ghfdb.importers import import_ghfdb_template

        xlsx_bytes = _build_official_xlsx(
            headers=list(ROW.keys()), data_rows=[list(ROW.values())]
        )

        outcome = import_ghfdb_template(xlsx_bytes, dataset)

        assert not outcome.has_errors(), (
            outcome.parent.invalid_rows,
            outcome.child.invalid_rows,
        )
        site = HeatFlowSite.objects.get(name="Test Site Alpha")
        parent = ParentHeatFlow.objects.get(ghfdb_id=1)
        child = HeatFlow.objects.get(ghfdb_id=1)
        assert parent.dataset_id == dataset.pk
        assert site.dataset_id == dataset.pk
        assert child.dataset_id == dataset.pk
        assert child.parent_id == parent.pk

    def test_accepts_an_already_parsed_dataset(self, dataset):
        """A caller already holding a parsed tablib.Dataset (the admin
        import wizard, for instance) can pass it straight through."""
        from heat_flow.models import HeatFlow, ParentHeatFlow

        from project.ghfdb.importers import import_ghfdb_template

        outcome = import_ghfdb_template(make_dataset(ROW), dataset)

        assert not outcome.has_errors(), (
            outcome.parent.invalid_rows,
            outcome.child.invalid_rows,
        )
        assert ParentHeatFlow.objects.filter(ghfdb_id=1).exists()
        assert HeatFlow.objects.filter(ghfdb_id=1).exists()

    def test_a_second_row_at_a_different_coordinate_pair_is_not_lost(self, dataset):
        """The parent resource's before_import() deduplicates its own
        working copy of the rows; the child pass must still see every row,
        proving each pass gets its own copy rather than sharing one that
        the parent pass has already mutated."""
        from heat_flow.models import HeatFlow

        from project.ghfdb.importers import import_ghfdb_template

        second_row = dict(ROW)
        second_row["ID_parent"] = "2"
        second_row["ID"] = "2"
        second_row["name"] = "Test Site Beta"
        second_row["lat_NS"] = "50.0"
        second_row["long_EW"] = "8.0"

        outcome = import_ghfdb_template(make_dataset(ROW, second_row), dataset)

        assert not outcome.has_errors(), (
            outcome.parent.invalid_rows,
            outcome.child.invalid_rows,
        )
        assert HeatFlow.objects.filter(ghfdb_id=1).exists()
        assert HeatFlow.objects.filter(ghfdb_id=2).exists()

    def test_refuses_when_no_dataset_is_named(self, dataset):
        """FR-002 holds through the entry point too: a dataset existing in
        the database is not enough, the caller must name it. Reported as a
        base error on the outcome — the same channel every other
        ``import_data()`` fault in this codebase is read from — rather than
        a raised exception, since ``import_ghfdb_template`` does not pass
        ``raise_errors=True`` (T007/T008 already cover the raise at the
        ``before_import`` level directly)."""
        from heat_flow.models import HeatFlow, ParentHeatFlow

        from project.ghfdb.importers import import_ghfdb_template

        outcome = import_ghfdb_template(make_dataset(ROW), None)

        assert outcome.has_errors()
        assert not ParentHeatFlow.objects.exists()
        assert not HeatFlow.objects.exists()


@pytest.mark.django_db
class TestGHFDBTemplateRefusedWhole:
    """T021 — US-4/#203, reproducing #190: a fault on a later row must not
    leave an earlier row's data written. ``rollback_on_validation_errors``
    is declared today inside both resources' ``Meta``, a place
    ``import_data()`` never reads it from, so nothing enforces it."""

    def test_a_later_row_fault_does_not_roll_back_an_earlier_row(self, dataset):
        """Two child rows; the second (later) row carries a value the model
        cannot store. The first row's determination must not survive the
        import once the second row faults — today it does."""
        from heat_flow.models import HeatFlow

        from project.ghfdb.importers import import_ghfdb_template

        row1 = dict(ROW)
        row2 = dict(ROW)
        row2["ID_parent"] = "2"
        row2["ID"] = "2"
        row2["name"] = "Test Site Beta"
        row2["lat_NS"] = "50.0"
        row2["long_EW"] = "8.0"
        row2["qc"] = "not-a-number"

        import_ghfdb_template(make_dataset(row1, row2), dataset)

        assert not HeatFlow.objects.filter(ghfdb_id=1).exists(), (
            "row 1 was written even though row 2, later in the same file, "
            "carried a fault the model cannot store (#190)"
        )

    def test_two_widely_separated_faults_are_both_reported_and_nothing_lands(
        self, dataset
    ):
        """T024 — three rows: the first is entirely clean, the second and
        third each carry their own fault on the child side only — the
        parent side (site, parent heat flow) has no fault on any row at
        all. Both faults must be reported, each naming its own row and
        column, and nothing from either pass may land: a resource with no
        fault of its own must not commit just because the other resource
        failed (FR-010, FR-012)."""
        from heat_flow.models import HeatFlow, HeatFlowSite, ParentHeatFlow

        from project.ghfdb.importers import import_ghfdb_template

        row1 = dict(ROW)

        row2 = dict(ROW)
        row2["ID_parent"] = "2"
        row2["ID"] = "2"
        row2["name"] = "Test Site Beta"
        row2["lat_NS"] = "50.0"
        row2["long_EW"] = "8.0"
        row2["qc"] = "not-a-number"

        row3 = dict(ROW)
        row3["ID_parent"] = "3"
        row3["ID"] = "3"
        row3["name"] = "Test Site Gamma"
        row3["lat_NS"] = "52.0"
        row3["long_EW"] = "9.0"
        row3["qc_uncertainty"] = "also-not-a-number"

        outcome = import_ghfdb_template(make_dataset(row1, row2, row3), dataset)

        assert outcome.has_errors()
        assert outcome.child.has_validation_errors()
        rows_with_faults = {invalid.number for invalid in outcome.child.invalid_rows}
        assert rows_with_faults == {2, 3}, outcome.child.invalid_rows
        columns_with_faults = {
            column
            for invalid in outcome.child.invalid_rows
            for column in invalid.field_specific_errors
        }
        assert columns_with_faults == {"value", "uncertainty"}, (
            outcome.child.invalid_rows
        )

        assert not HeatFlowSite.objects.exists()
        assert not ParentHeatFlow.objects.exists()
        assert not HeatFlow.objects.exists()

    def test_a_clean_file_reports_nothing_and_every_row_lands(self, dataset):
        """T026 — three rows, no fault anywhere: nothing is reported, and
        the count of every kind of record this file describes matches the
        row count exactly, not merely "something exists"."""
        from heat_flow.models import HeatFlow, HeatFlowSite, ParentHeatFlow

        from project.ghfdb.importers import import_ghfdb_template

        row1 = dict(ROW)

        row2 = dict(ROW)
        row2["ID_parent"] = "2"
        row2["ID"] = "2"
        row2["name"] = "Test Site Beta"
        row2["lat_NS"] = "50.0"
        row2["long_EW"] = "8.0"

        row3 = dict(ROW)
        row3["ID_parent"] = "3"
        row3["ID"] = "3"
        row3["name"] = "Test Site Gamma"
        row3["lat_NS"] = "52.0"
        row3["long_EW"] = "9.0"

        outcome = import_ghfdb_template(make_dataset(row1, row2, row3), dataset)

        assert not outcome.has_errors(), (
            outcome.parent.invalid_rows,
            outcome.child.invalid_rows,
        )
        assert HeatFlowSite.objects.count() == 3
        assert ParentHeatFlow.objects.count() == 3
        assert HeatFlow.objects.count() == 3

    def test_an_empty_mandatory_model_field_names_its_row_and_column_and_refuses_the_file(
        self, dataset
    ):
        """T026a — FR-011's fourth fault type: a row leaving a mandatory
        model field empty. Before T022 this had no enforcement path at all
        (DR-002): the widget silently sets the attribute to ``None`` and,
        with ``clean_model_instances`` false, nothing ever called
        ``full_clean()`` to catch it — the row wrote with a blank value, or
        the database raised an unnamed, untranslated ``IntegrityError``
        (SQLite has no ``value``/``unit`` split column pair to violate
        here; the parent heat-flow ``value`` is what is left empty). The
        fault must name its row and column, in a translated message
        (Django's own ``full_clean()`` messages are already
        ``gettext``-translated), and refuse the whole file."""
        from django.utils.translation import gettext as _
        from heat_flow.models import HeatFlow, HeatFlowSite, ParentHeatFlow

        from project.ghfdb.importers import import_ghfdb_template

        row1 = dict(ROW)
        row1["q"] = ""

        outcome = import_ghfdb_template(make_dataset(row1), dataset)

        assert outcome.has_errors()
        assert outcome.parent.has_validation_errors()
        (invalid,) = outcome.parent.invalid_rows
        assert invalid.number == 1
        assert "value" in invalid.field_specific_errors
        assert invalid.field_specific_errors["value"] == [
            _("This field cannot be null.")
        ]

        assert not HeatFlowSite.objects.exists()
        assert not ParentHeatFlow.objects.exists()
        assert not HeatFlow.objects.exists()


@pytest.mark.django_db
class TestControlledVocabularyDecides:
    """T027 — US-5/#204: the portal's own concepts decide what a controlled-
    vocabulary column accepts, not the template's own vocabulary sheet."""

    def test_an_unrecognised_vocabulary_value_names_row_column_and_value_and_refuses_the_file(
        self, dataset
    ):
        """A single-valued controlled-vocabulary column (``environment``)
        carrying a value the portal holds no concept for refuses the whole
        file, and the fault names the row, the column and the unrecognised
        value."""
        from heat_flow.models import HeatFlow, HeatFlowSite, ParentHeatFlow

        from project.ghfdb.importers import import_ghfdb_template

        row1 = dict(ROW)
        row1["environment"] = "not_a_real_value"

        outcome = import_ghfdb_template(make_dataset(row1), dataset)

        assert outcome.has_errors()
        row_number, errors = outcome.parent.row_errors()[0]
        assert row_number == 1
        message = str(errors[0].error)
        assert "environment" in message
        assert "not_a_real_value" in message

        assert not HeatFlowSite.objects.exists()
        assert not ParentHeatFlow.objects.exists()
        assert not HeatFlow.objects.exists()

    def test_an_unrecognised_value_in_a_many_valued_column_refuses_the_file(
        self, dataset
    ):
        """T028b — the rule holds through the many-valued path too. Every
        many-valued controlled-vocabulary column reaches
        ``MultiConceptWidget.clean`` through
        ``RelatedModelWidget.set_m2m_relations``, not through the scalar
        path T027/T028 cover — ``tc_method`` is one of the thirteen columns
        that path serves. Deliberately not a single-valued column like
        ``environment``: a test written against one of those would pass
        over the top of the defect T028a fixes (D6/DR-001)."""
        from heat_flow.models import (
            HeatFlow,
            HeatFlowSite,
            IntervalConductivity,
            ParentHeatFlow,
        )

        from project.ghfdb.importers import import_ghfdb_template

        row1 = dict(ROW)
        row1["tc_mean"] = "2.5"
        row1["tc_method"] = "not_a_real_method"

        outcome = import_ghfdb_template(make_dataset(row1), dataset)

        assert outcome.has_errors()
        row_number, errors = outcome.child.row_errors()[0]
        assert row_number == 1
        message = str(errors[0].error)
        assert "tc_method" in message
        assert "not_a_real_method" in message

        assert not HeatFlowSite.objects.exists()
        assert not ParentHeatFlow.objects.exists()
        assert not HeatFlow.objects.exists()
        assert not IntervalConductivity.objects.exists()

    def test_a_value_the_templates_sheet_lists_but_the_portal_does_not_hold_is_still_refused(
        self, dataset, official_upload_template_workbook
    ):
        """T029 — FR-014, stated backwards on purpose: a value straight
        from the official template's own 'controlled vocabulary' sheet —
        the sheet lists it, the portal holds no concept for it — still
        refuses the file. The value is read from the real fixture's sheet
        at test time, never hard-coded, so the test cannot pass by
        accident on a value absent from both."""
        from heat_flow import vocabularies
        from heat_flow.models import HeatFlow, HeatFlowSite, ParentHeatFlow
        from research_vocabs.models import Concept

        from project.ghfdb.importers import import_ghfdb_template
        from project.ghfdb.resources.widgets import normalize_vocab_token

        ws = official_upload_template_workbook["controlled vocabulary"]
        rows = list(ws.iter_rows(values_only=True))
        header = rows[0]
        idx = header.index("Type of exploration method")
        sheet_values = {
            normalize_vocab_token(cell) for cell in (r[idx] for r in rows[2:]) if cell
        }
        portal_labels = {
            label.lower()
            for label in Concept.get_for_vocabulary(
                vocabularies.ExplorationMethod
            ).values_list("label", flat=True)
        }
        only_on_sheet = sorted(sheet_values - portal_labels)
        assert only_on_sheet, (
            "expected the template's vocabulary sheet to list at least "
            "one value the portal holds no concept for"
        )
        value = only_on_sheet[0]

        row1 = dict(ROW)
        row1["explo_method"] = value

        outcome = import_ghfdb_template(make_dataset(row1), dataset)

        assert outcome.has_errors()
        assert not HeatFlowSite.objects.exists()
        assert not ParentHeatFlow.objects.exists()
        assert not HeatFlow.objects.exists()

    def test_a_value_the_portal_holds_but_the_templates_sheet_does_not_list_is_accepted(
        self, dataset, official_upload_template_workbook
    ):
        """T030 — the other half of FR-013/FR-014: a value the portal
        holds a concept for, which the template's own sheet does not
        list, is accepted and the row lands. The value is read from the
        real fixture's sheet, the same way T029's is."""
        from heat_flow import vocabularies
        from heat_flow.models import HeatFlow
        from research_vocabs.models import Concept

        from project.ghfdb.importers import import_ghfdb_template
        from project.ghfdb.resources.widgets import normalize_vocab_token

        ws = official_upload_template_workbook["controlled vocabulary"]
        rows = list(ws.iter_rows(values_only=True))
        header = rows[0]
        idx = header.index("Heat-flow method")
        sheet_values = {
            normalize_vocab_token(cell) for cell in (r[idx] for r in rows[2:]) if cell
        }
        portal_labels = {
            label.lower()
            for label in Concept.get_for_vocabulary(
                vocabularies.HeatFlowMethod
            ).values_list("label", flat=True)
        }
        only_in_portal = sorted(portal_labels - sheet_values)
        assert only_in_portal, (
            "expected the portal to hold at least one concept the "
            "template's vocabulary sheet does not list"
        )
        value = only_in_portal[0]

        row1 = dict(ROW)
        row1["q_method"] = value

        outcome = import_ghfdb_template(make_dataset(row1), dataset)

        assert not outcome.has_errors(), (
            outcome.parent.invalid_rows,
            outcome.child.invalid_rows,
        )
        child = HeatFlow.objects.get(ghfdb_id=1)
        assert value in {
            label.lower() for label in child.method.values_list("label", flat=True)
        }

    def test_the_import_never_opens_the_controlled_vocabulary_sheet(self, dataset):
        """T031 — proven by sheet name, not by hoping: wraps the real
        ``openpyxl.load_workbook()`` call the reader makes while importing
        the real, unmodified template fixture, and records every sheet
        name reached through ``Workbook.__getitem__``. A future change
        that starts honouring the sheet fails here."""
        from pathlib import Path
        from unittest import mock

        import openpyxl

        from project.ghfdb.importers import import_ghfdb_template

        accessed_sheets = []
        real_load_workbook = openpyxl.load_workbook

        class _TrackingWorkbook:
            def __init__(self, wb):
                self._wb = wb

            def __getitem__(self, name):
                accessed_sheets.append(name)
                return self._wb[name]

            def __getattr__(self, name):
                return getattr(self._wb, name)

        def _tracking_load_workbook(*args, **kwargs):
            return _TrackingWorkbook(real_load_workbook(*args, **kwargs))

        path = (
            Path(__file__).resolve().parents[1]
            / "fixtures"
            / "official_upload_template.xlsx"
        )
        xlsx_bytes = path.read_bytes()

        with mock.patch("openpyxl.load_workbook", side_effect=_tracking_load_workbook):
            import_ghfdb_template(xlsx_bytes, dataset)

        assert "data list" in accessed_sheets
        assert "controlled vocabulary" not in accessed_sheets
