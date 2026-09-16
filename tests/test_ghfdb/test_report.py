"""Tests for project.ghfdb.report (T009).

Turns a ``GHFDBImportOutcome`` into the counts and per-row failures FR-009
and FR-012 need: sites separated from determinations, created separated
from updated, and each failure naming its row, its column and a specific
reason.
"""

import pytest

from tests.test_ghfdb.test_importers import ROW, make_dataset


@pytest.mark.django_db
class TestBuildReportCounts:
    def test_counts_separate_sites_from_determinations_and_created_from_updated(
        self, dataset
    ):
        from project.ghfdb.importers import import_ghfdb_template
        from project.ghfdb.report import build_report

        row = {k: v for k, v in ROW.items() if k not in ("ID", "ID_parent")}
        import_ghfdb_template(make_dataset(row), dataset)

        row2 = dict(ROW)
        row2["ID_parent"] = "2"
        row2["ID"] = "2"
        row2["name"] = "Test Site Beta"
        row2["lat_NS"] = "50.0"
        row2["long_EW"] = "8.0"
        unchanged = {k: v for k, v in ROW.items() if k not in ("ID", "ID_parent")}

        outcome = import_ghfdb_template(make_dataset(unchanged, row2), dataset)
        report = build_report(outcome)

        assert report.sites_created == 1
        assert report.sites_updated == 1
        assert report.determinations_created == 1
        assert report.determinations_updated == 1

    def test_a_clean_multi_row_file_reports_only_creation_counts(self, dataset):
        from project.ghfdb.importers import import_ghfdb_template
        from project.ghfdb.report import build_report

        row2 = dict(ROW)
        row2["ID_parent"] = "2"
        row2["ID"] = "2"
        row2["name"] = "Test Site Beta"
        row2["lat_NS"] = "50.0"
        row2["long_EW"] = "8.0"

        outcome = import_ghfdb_template(
            make_dataset(ROW, row2), dataset, check_only=True
        )
        report = build_report(outcome)

        assert report.sites_created == 2
        assert report.sites_updated == 0
        assert report.determinations_created == 2
        assert report.determinations_updated == 0
        assert not report.has_failures


@pytest.mark.django_db
class TestBuildReportFailures:
    def test_a_vocabulary_failure_carries_its_row_and_column(self, dataset):
        from project.ghfdb.importers import import_ghfdb_template
        from project.ghfdb.report import build_report

        row1 = dict(ROW)
        row1["environment"] = "not_a_real_value"

        outcome = import_ghfdb_template(make_dataset(row1), dataset, check_only=True)
        report = build_report(outcome)

        assert report.has_failures
        failure = report.failures[0]
        assert failure.row_number == 1
        assert failure.column == "environment"
        assert "not_a_real_value" in failure.reason

    def test_an_empty_mandatory_field_failure_carries_the_templates_column_name(
        self, dataset
    ):
        """The full_clean() validation error names the Django model field
        ("value"); the report must translate that back to the template's
        own column heading ("q")."""
        from project.ghfdb.importers import import_ghfdb_template
        from project.ghfdb.report import build_report

        row1 = dict(ROW)
        row1["q"] = ""

        outcome = import_ghfdb_template(make_dataset(row1), dataset, check_only=True)
        report = build_report(outcome)

        assert report.has_failures
        failure = report.failures[0]
        assert failure.row_number == 1
        assert failure.column == "q"

    def test_a_scalar_vocabulary_failure_names_the_value_and_the_vocabulary(
        self, dataset
    ):
        """T010/FR-012: a bare 'invalid value' does not satisfy this — the
        reason must name both the supplied value and the vocabulary it was
        checked against."""
        from project.ghfdb.importers import import_ghfdb_template
        from project.ghfdb.report import build_report

        row1 = dict(ROW)
        row1["environment"] = "not_a_real_value"

        outcome = import_ghfdb_template(make_dataset(row1), dataset, check_only=True)
        report = build_report(outcome)

        # The child pass also reports a fault of its own here — it cannot
        # resolve the parent the environment fault kept from being created —
        # so this asserts on the environment failure specifically rather
        # than assuming it is the only one.
        failure = next(f for f in report.failures if f.column == "environment")
        assert "not_a_real_value" in failure.reason
        assert "GeographicEnvironment" in failure.reason

    def test_a_many_valued_vocabulary_failure_names_the_value_and_the_vocabulary(
        self, dataset
    ):
        """The many-valued path (``tc_method``, via
        ``RelatedModelWidget.set_m2m_relations``) must carry the same two
        facts as the scalar path."""
        from project.ghfdb.importers import import_ghfdb_template
        from project.ghfdb.report import build_report

        row1 = dict(ROW)
        row1["tc_mean"] = "2.5"
        row1["tc_method"] = "not_a_real_method"

        outcome = import_ghfdb_template(make_dataset(row1), dataset, check_only=True)
        report = build_report(outcome)

        (failure,) = report.failures
        assert "not_a_real_method" in failure.reason
        assert "ConductivityMethod" in failure.reason

    def test_a_related_widget_failure_does_not_name_the_model_it_wraps(self, dataset):
        """T028, FR-013: ``RelatedModelWidget`` wraps a sub-field's error
        with its own Django model's class name (``ParentWidget`` ->
        ``HeatFlowSite``) so a developer reading raw output can place the
        fault — that name is internal and must not reach the report."""
        from project.ghfdb.importers import import_ghfdb_template
        from project.ghfdb.report import build_report

        row1 = dict(ROW)
        row1["environment"] = "not_a_real_value"

        outcome = import_ghfdb_template(make_dataset(row1), dataset, check_only=True)
        report = build_report(outcome)

        failure = next(f for f in report.failures if f.column == "environment")
        assert "HeatFlowSite" not in failure.reason
        assert "not_a_real_value" in failure.reason
        assert "GeographicEnvironment" in failure.reason

    def test_a_downstream_parent_resolution_failure_does_not_name_the_model_class(
        self, dataset
    ):
        """T028, FR-013: when a row's parent failed to import, the child
        pass's own ``ForeignKeyWidget`` cannot resolve it and raises
        Django's own ``DoesNotExist``, whose default message names the
        model class directly — that must not reach the report either."""
        from project.ghfdb.importers import import_ghfdb_template
        from project.ghfdb.report import build_report

        row1 = dict(ROW)
        row1["environment"] = "not_a_real_value"

        outcome = import_ghfdb_template(make_dataset(row1), dataset, check_only=True)
        report = build_report(outcome)

        assert report.has_failures
        for failure in report.failures:
            assert "ParentHeatFlow" not in failure.reason
            assert "matching query does not exist" not in failure.reason

    def test_multiple_failures_are_all_reported(self, dataset):
        from project.ghfdb.importers import import_ghfdb_template
        from project.ghfdb.report import build_report

        row2 = dict(ROW)
        row2["ID_parent"] = "2"
        row2["ID"] = "2"
        row2["name"] = "Test Site Gamma"
        row2["lat_NS"] = "52.0"
        row2["long_EW"] = "9.0"
        row2["qc"] = "not-a-number"

        row3 = dict(ROW)
        row3["ID_parent"] = "3"
        row3["ID"] = "3"
        row3["name"] = "Test Site Delta"
        row3["lat_NS"] = "53.0"
        row3["long_EW"] = "10.0"
        row3["qc_uncertainty"] = "also-not-a-number"

        outcome = import_ghfdb_template(
            make_dataset(row2, row3), dataset, check_only=True
        )
        report = build_report(outcome)

        assert len(report.failures) == 2
        rows_with_faults = {failure.row_number for failure in report.failures}
        assert rows_with_faults == {1, 2}
        columns_with_faults = {failure.column for failure in report.failures}
        assert columns_with_faults == {"qc", "qc_uncertainty"}
