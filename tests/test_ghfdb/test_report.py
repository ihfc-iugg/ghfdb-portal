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
