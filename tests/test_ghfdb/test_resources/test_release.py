"""
Tests for project/ghfdb/resources/release.py (specs/003-ghfdb-release-import).

Phase 2 - US-1, first part: a release file is checked in full before
anything is written (T008, T009, T011-T024, T033). The reader this module
tests does not yet turn a row into the site, interval and determination it
describes (US-3) or create the dataset and literature a row's publication
reference resolves to (US-2) - this story checks a file and reports its
faults.
"""

import csv
from pathlib import Path

import pytest
import tablib
from fairdm.core.models import Dataset
from literature.models import LiteratureItem

from project.ghfdb.constants import MISSPELLED_COLUMNS
from project.ghfdb.resources.release import (
    GHFDBReleaseCSVFormat,
    GHFDBReleaseImportResource,
)

pytestmark = pytest.mark.ghfdb

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "release"
BASE_FIXTURE = FIXTURES_DIR / "release_sample.csv"


def _corrected_header_and_rows():
    """BASE_FIXTURE's header and data rows, with the two misspelled
    published names corrected (MISSPELLED_COLUMNS) - the file a curator
    would submit after preparing it, not the archive as downloaded (D7).
    """
    text = BASE_FIXTURE.read_text(encoding="utf-8-sig")
    reader = csv.reader(text.splitlines())
    header = [MISSPELLED_COLUMNS.get(name, name) for name in next(reader)]
    rows = list(reader)
    return header, rows


def _make_dataset(header, rows):
    dataset = tablib.Dataset(headers=header)
    for row in rows:
        dataset.append(row)
    return dataset


def _corrected_dataset():
    """A tablib Dataset built from the corrected base fixture, unmodified."""
    header, rows = _corrected_header_and_rows()
    return _make_dataset(header, rows)


def _dataset_from_fixture(path):
    """A tablib Dataset built from a fixture file's header and rows exactly
    as written - no correction applied."""
    text = path.read_text(encoding="utf-8-sig")
    reader = csv.reader(text.splitlines())
    header = next(reader)
    rows = list(reader)
    return _make_dataset(header, rows)


def _with_cell(header, rows, row_index, column, value):
    """``rows`` with a single cell replaced, by column name and row
    position - the rest of the row untouched."""
    changed = [list(row) for row in rows]
    changed[row_index][header.index(column)] = value
    return changed


def _without_column(header, rows, column):
    """``header`` and ``rows`` with one column dropped from both, so the
    result stays a well-formed (non-ragged) dataset."""
    index = header.index(column)
    new_header = header[:index] + header[index + 1 :]
    new_rows = [row[:index] + row[index + 1 :] for row in rows]
    return new_header, new_rows


class TestGHFDBReleaseCSVFormat:
    """T009: the reading format is a comma-separated reader carrying a name
    a curator can recognise, reading the header from the first line and the
    data from the second."""

    def test_get_title_is_curator_recognisable(self):
        assert GHFDBReleaseCSVFormat().get_title() == "GHFDB Release Format"

    def test_reads_the_header_from_the_first_line_and_data_from_the_second(self):
        csv_bytes = "ID,qc\nR24-000001,48.1\nR24-000002,84.1\n".encode("utf-8-sig")
        dataset = GHFDBReleaseCSVFormat(encoding="utf-8-sig").create_dataset(csv_bytes)

        assert dataset.headers == ["ID", "qc"]
        assert dataset.dict == [
            {"ID": "R24-000001", "qc": "48.1"},
            {"ID": "R24-000002", "qc": "84.1"},
        ]


class TestGHFDBReleaseImportResourceCleanFile:
    """T008: a release file whose header is the real published one passes
    the column check and its values are read."""

    def test_clean_file_passes_the_column_check_and_its_values_are_read(self):
        header, rows = _corrected_header_and_rows()
        dataset = _make_dataset(header, rows)

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=True, raise_errors=False)

        assert result.has_errors() is False
        assert result.has_validation_errors() is False
        assert result.total_rows == len(rows)


class TestGHFDBReleaseImportResourceMisspelledColumns:
    """T011, T012: a file carrying a misspelled published column name is
    refused, the error names the misspelled name, the correct name and the
    outdated template, and no record of any kind is created. Asserted
    separately for each of the two misspelled names (SC-001), so a check
    keyed to one cannot leave the other unrefused, and the refusal holds
    without exception for the published release itself, which carries both
    (D7)."""

    def test_only_ref_isgn_misspelled_is_refused(self):
        dataset = _dataset_from_fixture(
            FIXTURES_DIR / "header_misspelled_only_ref_isgn.csv"
        )
        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=True, raise_errors=False)

        assert result.has_errors() is True
        message = str(result.base_errors[0].error)
        assert "Ref_ISGN" in message
        assert "Ref_IGSN" in message
        assert "outdated" in message
        assert result.total_rows == 0

    def test_only_tc_pt_fuction_misspelled_is_refused(self):
        dataset = _dataset_from_fixture(
            FIXTURES_DIR / "header_misspelled_only_tc_pt_fuction.csv"
        )
        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=True, raise_errors=False)

        assert result.has_errors() is True
        message = str(result.base_errors[0].error)
        assert "tc_pT_fuction" in message
        assert "tc_pT_function" in message
        assert "outdated" in message
        assert result.total_rows == 0

    def test_published_release_header_carrying_both_misspellings_is_refused(self, db):
        """D7: the refusal holds without exception, including for the
        published release itself, which carries both misspelled names, and
        no record of any kind is created."""
        from heat_flow.models import HeatFlow

        dataset = _dataset_from_fixture(BASE_FIXTURE)
        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_errors() is True
        message = str(result.base_errors[0].error)
        assert "Ref_ISGN" in message
        assert "Ref_IGSN" in message
        assert "tc_pT_fuction" in message
        assert "tc_pT_function" in message
        assert result.total_rows == 0
        assert HeatFlow.objects.count() == 0


class TestGHFDBReleaseImportResourceUndefinedColumn:
    """T013, T014: a file carrying a column name the release format does
    not define is refused with that column named."""

    def test_undefined_column_is_refused_and_named(self):
        dataset = _dataset_from_fixture(FIXTURES_DIR / "header_undefined_column.csv")
        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=True, raise_errors=False)

        assert result.has_errors() is True
        message = str(result.base_errors[0].error)
        assert "p_comment_extra" in message
        assert result.total_rows == 0


class TestGHFDBReleaseImportResourceMissingColumn:
    """T015, T016: a file missing a column the release format requires is
    refused with that column named."""

    def test_missing_required_column_is_refused_and_named(self):
        """The fixture drops only the header cell (T005), leaving its data
        rows one column wider than the new header - read through the
        format itself, as a curator's upload would be, rather than built
        by hand."""
        path = FIXTURES_DIR / "header_missing_required_column.csv"
        dataset = GHFDBReleaseCSVFormat(encoding="utf-8-sig").create_dataset(
            path.read_bytes()
        )

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=True, raise_errors=False)

        assert result.has_errors() is True
        message = str(result.base_errors[0].error)
        assert "environment" in message
        assert result.total_rows == 0


class TestGHFDBReleaseImportResourceReportsEveryFault:
    """T019: a file whose header is correct but whose rows carry faults in
    several different rows reports every fault, not the first."""

    def test_every_faulty_row_is_reported(self):
        header, rows = _corrected_header_and_rows()
        rows = _with_cell(header, rows, 0, "qc", "not-a-number")
        rows = _with_cell(header, rows, 2, "qc_uncertainty", "also-not-a-number")
        dataset = _make_dataset(header, rows)

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=True, raise_errors=False)

        assert result.has_validation_errors() is True
        assert len(result.invalid_rows) == 2
        faulty_row_numbers = {row.number for row in result.invalid_rows}
        assert faulty_row_numbers == {2, 4}


class TestGHFDBReleaseImportResourceLineNumber:
    """T020, T021: a reported fault carries the row number as it appears
    in the file, counting the header line, so a fault in the first data
    row reports as line 2."""

    def test_fault_in_the_first_data_row_reports_as_line_two(self):
        header, rows = _corrected_header_and_rows()
        rows = _with_cell(header, rows, 0, "qc", "not-a-number")
        dataset = _make_dataset(header, rows)

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=True, raise_errors=False)

        assert len(result.invalid_rows) == 1
        assert result.invalid_rows[0].number == 2

    def test_fault_in_the_third_data_row_reports_as_line_four(self):
        header, rows = _corrected_header_and_rows()
        rows = _with_cell(header, rows, 2, "qc", "not-a-number")
        dataset = _make_dataset(header, rows)

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=True, raise_errors=False)

        assert len(result.invalid_rows) == 1
        assert result.invalid_rows[0].number == 4


class TestGHFDBReleaseImportResourceColumnName:
    """T022, T023: a reported fault names the column as it appears in the
    header, not the model attribute the value would have been stored in -
    for every column that can refuse a value."""

    @pytest.mark.parametrize(
        ("column",),
        [
            ("qc",),
            ("qc_uncertainty",),
        ],
    )
    def test_fault_is_keyed_by_the_column_name(self, column):
        header, rows = _corrected_header_and_rows()
        rows = _with_cell(header, rows, 0, column, "not-a-number")
        dataset = _make_dataset(header, rows)

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=True, raise_errors=False)

        assert len(result.invalid_rows) == 1
        error_dict = result.invalid_rows[0].error_dict
        assert column in error_dict
        # The model attribute a curator never sees must not appear instead.
        attribute = {"qc": "value", "qc_uncertainty": "uncertainty"}[column]
        assert attribute not in error_dict


class TestGHFDBReleaseImportResourceValueAndReason:
    """T024: a reported fault carries the offending value and a reason
    that distinguishes it from other reasons."""

    def test_fault_carries_the_offending_value(self):
        header, rows = _corrected_header_and_rows()
        rows = _with_cell(header, rows, 0, "qc", "not-a-number")
        dataset = _make_dataset(header, rows)

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=True, raise_errors=False)

        message = str(result.invalid_rows[0].error_dict["qc"][0])
        assert "not-a-number" in message

    def test_two_different_offending_values_carry_two_different_messages(self):
        """The reason is not a generic, value-independent label - a
        curator reading two faults for the same column can tell them
        apart, because each message names the value that was refused."""
        header, rows = _corrected_header_and_rows()
        first_dataset = _make_dataset(
            header, _with_cell(header, rows, 0, "qc", "not-a-number")
        )
        second_dataset = _make_dataset(
            header, _with_cell(header, rows, 0, "qc", "48.1kg")
        )

        resource = GHFDBReleaseImportResource()
        first_result = resource.import_data(
            first_dataset, dry_run=True, raise_errors=False
        )
        second_result = resource.import_data(
            second_dataset, dry_run=True, raise_errors=False
        )

        first_message = str(first_result.invalid_rows[0].error_dict["qc"][0])
        second_message = str(second_result.invalid_rows[0].error_dict["qc"][0])
        assert first_message != second_message


class TestGHFDBReleaseImportResourceHeaderFailureStopsTheRowLoop:
    """T017, T018: after a header refusal, no data row was read at all -
    proven by a row that would itself have raised, which produces no
    second error."""

    def test_no_row_is_read_after_a_header_refusal(self):
        header, rows = _corrected_header_and_rows()
        rows = _with_cell(header, rows, 0, "qc", "not-a-number")
        header_with_fault, rows_with_fault = _without_column(
            header, rows, "environment"
        )
        dataset = _make_dataset(header_with_fault, rows_with_fault)

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=True, raise_errors=False)

        assert result.has_errors() is True
        assert "environment" in str(result.base_errors[0].error)
        assert result.invalid_rows == []
        assert result.error_rows == []
        assert result.total_rows == 0


class TestGHFDBReleaseImportResourceDatasetCreation:
    """T034, T035, T036: a file whose rows carry several distinct
    publication references produces one dataset for each reference. Fails
    before: no dataset is created by reading a file.

    The full acceptance sentence also requires that no dataset holds
    records from two - the second half needs a row to have become a
    record, which is US-3's job (save_instance stays a no-op in this
    story). What this story reaches is asserted here: each reference
    resolves to its own distinct dataset."""

    def test_one_dataset_per_distinct_publication_reference(self, db):
        header, rows = _corrected_header_and_rows()
        reference_index = header.index("publication_reference")
        references = {row[reference_index] for row in rows}
        dataset = _make_dataset(header, rows)

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_errors() is False
        assert result.has_validation_errors() is False
        release_datasets = Dataset.all_objects.filter(reference__isnull=False)
        assert release_datasets.count() == len(references)
        assert {d.reference.citation_key for d in release_datasets} == references


class TestGHFDBReleaseImportResourceReferenceNormalization:
    """T037, T038: two references differing only by case or by surrounding
    whitespace are one reference, and produce one dataset. Fails before:
    they produce two."""

    def test_references_differing_by_case_and_whitespace_produce_one_dataset(self, db):
        header, rows = _corrected_header_and_rows()
        reference_index = header.index("publication_reference")
        distinct_references = {row[reference_index] for row in rows}
        canonical_reference = rows[0][reference_index]
        varied_rows = _with_cell(
            header,
            rows,
            3,
            "publication_reference",
            f"  {canonical_reference.upper()}  ",
        )
        dataset = _make_dataset(header, varied_rows)

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_errors() is False
        assert result.has_validation_errors() is False
        matching = Dataset.all_objects.filter(
            reference__citation_key=canonical_reference
        )
        assert matching.count() == 1
        assert (
            Dataset.all_objects.filter(reference__isnull=False).count()
            == len(distinct_references) - 1
        )


class TestGHFDBReleaseImportResourceMatchesExistingLiterature:
    """T039, T040: a reference matching exactly one bibliographic record
    gives its dataset that record's title, and links the two. Fails
    before: no bibliographic record is consulted."""

    def test_matching_reference_links_and_titles_the_dataset(
        self, db, literature_with_known_citation_key
    ):
        header, rows = _corrected_header_and_rows()
        rows = _with_cell(
            header,
            rows,
            0,
            "publication_reference",
            literature_with_known_citation_key.citation_key,
        )
        dataset = _make_dataset(header, rows)

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_errors() is False
        assert result.has_validation_errors() is False
        release_dataset = Dataset.all_objects.get(
            reference=literature_with_known_citation_key
        )
        assert release_dataset.name == literature_with_known_citation_key.title


class TestGHFDBReleaseImportResourceCreatesMissingLiterature:
    """T041, T042: a reference matching no bibliographic record creates one
    carrying that citation key, and the dataset links to it. Fails before:
    nothing is created."""

    def test_unmatched_reference_creates_a_bibliographic_record(self, db):
        header, rows = _corrected_header_and_rows()
        new_reference = "Unknown_Author_1999"
        rows = _with_cell(header, rows, 0, "publication_reference", new_reference)
        dataset = _make_dataset(header, rows)

        assert not LiteratureItem.objects.filter(citation_key=new_reference).exists()

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_errors() is False
        assert result.has_validation_errors() is False
        literature_item = LiteratureItem.objects.get(citation_key=new_reference)
        release_dataset = Dataset.all_objects.get(reference=literature_item)
        assert release_dataset.reference == literature_item


class TestGHFDBReleaseImportResourceAmbiguousReference:
    """T043, T044: a reference matching more than one bibliographic record
    refuses the rows carrying it, naming the reference and the records it
    matched, and creates neither a dataset nor a record. Fails before: the
    first match is taken."""

    def test_ambiguous_reference_refuses_its_rows_and_creates_nothing(
        self, db, literature_with_ambiguous_citation_key
    ):
        first, second = literature_with_ambiguous_citation_key
        header, rows = _corrected_header_and_rows()
        ambiguous_reference = "Glaeser_1983_Heat_Flow"
        rows = _with_cell(header, rows, 0, "publication_reference", ambiguous_reference)
        rows = _with_cell(header, rows, 1, "publication_reference", ambiguous_reference)
        dataset = _make_dataset(header, rows)

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_validation_errors() is True
        refused = {row.number: row for row in result.invalid_rows}
        assert {2, 3}.issubset(refused)
        for number in (2, 3):
            message = str(refused[number].error_dict["publication_reference"][0])
            assert ambiguous_reference in message
            assert first.citation_key in message
            assert second.citation_key in message

        assert not Dataset.all_objects.filter(reference__in=[first, second]).exists()
        assert (
            LiteratureItem.objects.filter(
                citation_key__in=[first.citation_key, second.citation_key]
            ).count()
            == 2
        )


class TestGHFDBReleaseImportResourceEmptyReference:
    """T045, T046: a row whose publication reference is empty is refused.
    Fails before: it is filed under a default."""

    def test_empty_publication_reference_is_refused(self, db):
        header, rows = _corrected_header_and_rows()
        rows = _with_cell(header, rows, 0, "publication_reference", "")
        dataset = _make_dataset(header, rows)

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_validation_errors() is True
        refused = {row.number: row for row in result.invalid_rows}
        assert 2 in refused
        assert "publication_reference" in refused[2].error_dict


class TestGHFDBReleaseImportResourceReferenceReadback:
    """T047, T048: the publication reference a dataset was created from
    can be read back off the dataset, rather than recovered by inspecting
    its records. Fails before: it is not stored.

    Per plan.md this goes through the dataset's existing one-to-one link
    to a bibliographic record, so the citation key is one hop away and no
    model change is needed - no records exist to inspect in this story
    anyway (save_instance is a no-op), so the read-back is proven directly
    off ``dataset.reference``."""

    def test_the_reference_reads_back_off_the_dataset(self, db):
        header, rows = _corrected_header_and_rows()
        reference_index = header.index("publication_reference")
        reference = rows[0][reference_index]
        dataset = _make_dataset(header, rows)

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_errors() is False
        release_dataset = Dataset.all_objects.get(reference__citation_key=reference)
        assert release_dataset.reference.citation_key == reference


class TestGHFDBReleaseImportResourceReusesExistingDatasets:
    """T049: a file whose references already have datasets from an
    earlier import reuses them and creates no duplicates. Fails before: a
    second set is created."""

    def test_reimporting_the_same_file_creates_no_duplicate_datasets(self, db):
        header, rows = _corrected_header_and_rows()

        first_result = GHFDBReleaseImportResource().import_data(
            _make_dataset(header, rows), dry_run=False, raise_errors=False
        )
        assert first_result.has_errors() is False

        dataset_count_after_first = Dataset.all_objects.filter(
            reference__isnull=False
        ).count()
        literature_count_after_first = LiteratureItem.objects.count()

        second_result = GHFDBReleaseImportResource().import_data(
            _make_dataset(header, rows), dry_run=False, raise_errors=False
        )
        assert second_result.has_errors() is False

        assert (
            Dataset.all_objects.filter(reference__isnull=False).count()
            == dataset_count_after_first
        )
        assert LiteratureItem.objects.count() == literature_count_after_first


class TestGHFDBReleaseImportResourceCheckCreatesNothingPersistent:
    """T050: nothing created while checking a file survives the check - a
    dataset the check would have made does not exist afterwards. Fails
    before: the resolution runs once and its result is carried into the
    write. The check and the write are separate passes over separate
    objects (research.md R4)."""

    def test_dry_run_leaves_no_dataset_or_literature_record_behind(self, db):
        header, rows = _corrected_header_and_rows()
        dataset = _make_dataset(header, rows)

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=True, raise_errors=False)

        assert result.has_errors() is False
        assert Dataset.all_objects.filter(reference__isnull=False).count() == 0
        assert LiteratureItem.objects.count() == 0


class TestGHFDBReleaseImportResourceRecordGraph:
    """T051-T055: one valid row produces a site, an interval, a
    determination, and the gradient and conductivity measured over that
    interval, related as the model defines. Fails before: no reader
    exists - save_instance is a no-op."""

    def test_one_row_produces_the_full_record_graph(self, db):
        from heat_flow.models import (
            HeatFlow,
            HeatFlowInterval,
            HeatFlowSite,
            IntervalConductivity,
            ParentHeatFlow,
            ThermalGradient,
        )

        header, rows = _corrected_header_and_rows()
        row = _with_cell(header, rows, 4, "q_bottom", "4520.00")[4]
        dataset = _make_dataset(header, [row])

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_errors() is False
        assert result.has_validation_errors() is False

        site = HeatFlowSite.objects.get()
        assert site.local_id == "R24-P003477"
        assert site.name == "V19-6"

        parent = ParentHeatFlow.objects.get()
        assert parent.sample == site
        assert parent.local_id == "R24-P003477"
        assert float(parent.value.magnitude) == 50.0

        interval = HeatFlowInterval.objects.get()
        assert interval.site == site
        assert float(interval.top.magnitude) == 4490.0
        assert float(interval.bottom.magnitude) == 4520.0

        determination = HeatFlow.objects.get()
        assert determination.sample == interval
        assert determination.parent == parent
        assert determination.local_id == "R24-033563"
        assert float(determination.value.magnitude) == 48.0

        gradient = ThermalGradient.objects.get()
        assert determination.thermal_gradient == gradient
        assert gradient.sample == interval
        assert float(gradient.value.magnitude) == 58.0

        conductivity = IntervalConductivity.objects.get()
        assert determination.thermal_conductivity == conductivity
        assert conductivity.sample == interval
        assert float(conductivity.value.magnitude) == 0.83


class TestGHFDBReleaseImportResourceSharedSite:
    """T056, T057: several rows sharing a published site identifier
    produce one site carrying every determination, identified by that
    identifier alone. Fails before: each row makes its own site."""

    def test_rows_sharing_a_site_identifier_produce_one_site(self, db):
        from heat_flow.models import HeatFlow, HeatFlowSite

        header, rows = _corrected_header_and_rows()
        dataset = _make_dataset(header, [rows[0], rows[4]])

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_errors() is False
        assert result.has_validation_errors() is False

        assert HeatFlowSite.objects.count() == 1
        site = HeatFlowSite.objects.get(local_id="R24-P003477")
        determinations = HeatFlow.objects.filter(sample__in=site.intervals.all())
        assert determinations.count() == 2
        assert set(determinations.values_list("local_id", flat=True)) == {
            "R24-003627",
            "R24-033563",
        }


class TestGHFDBReleaseImportResourceSharedParent:
    """T058: the site's parent heat flow value is created once for the
    site and not once per row. Fails before: it is created per row."""

    def test_rows_sharing_a_site_share_one_parent_heat_flow_value(self, db):
        from heat_flow.models import HeatFlow, ParentHeatFlow

        header, rows = _corrected_header_and_rows()
        dataset = _make_dataset(header, [rows[0], rows[4]])

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_errors() is False
        assert result.has_validation_errors() is False

        assert ParentHeatFlow.objects.count() == 1
        parent = ParentHeatFlow.objects.get(local_id="R24-P003477")
        assert HeatFlow.objects.filter(parent=parent).count() == 2


class TestGHFDBReleaseImportResourceSharedInterval:
    """T059, T060: several rows giving one site and one depth range
    produce one interval, identified by its site and that depth range,
    carrying all of their determinations, each with its own gradient and
    conductivity. Fails before: each row makes its own interval. An
    interval is a sample in its own right and can be measured again by
    someone else (D15)."""

    def test_rows_sharing_a_site_and_depth_range_produce_one_interval(self, db):
        from heat_flow.models import (
            HeatFlow,
            HeatFlowInterval,
            IntervalConductivity,
            ThermalGradient,
        )

        header, rows = _corrected_header_and_rows()
        shared_rows = _with_cell(header, [rows[4], rows[5]], 0, "q_bottom", "4520.00")
        shared_rows = _with_cell(header, shared_rows, 1, "q_bottom", "4520.00")
        dataset = _make_dataset(header, shared_rows)

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_errors() is False
        assert result.has_validation_errors() is False

        assert HeatFlowInterval.objects.count() == 1
        interval = HeatFlowInterval.objects.get()
        determinations = HeatFlow.objects.filter(sample=interval)
        assert determinations.count() == 2
        assert set(determinations.values_list("local_id", flat=True)) == {
            "R24-033563",
            "R24-053075",
        }
        assert ThermalGradient.objects.filter(sample=interval).count() == 2
        assert IntervalConductivity.objects.filter(sample=interval).count() == 2


class TestGHFDBReleaseImportResourceIndeterminateInterval:
    """T061, T062: several rows giving one site and no depth range at
    all attach to one indeterminate interval for that site, one per
    site. Fails before: they produce one interval per row, or collapse
    into an interval that has a depth (D17)."""

    def test_rows_with_no_depth_share_the_sites_indeterminate_interval(self, db):
        from heat_flow.models import HeatFlow, HeatFlowInterval

        header, rows = _corrected_header_and_rows()
        dataset = _make_dataset(header, [rows[0], rows[1], rows[2]])

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_errors() is False
        assert result.has_validation_errors() is False

        assert HeatFlowInterval.objects.count() == 1
        interval = HeatFlowInterval.objects.get()
        assert interval.top is None
        assert interval.bottom is None
        assert HeatFlow.objects.filter(sample=interval).count() == 3


class TestGHFDBReleaseImportResourceGradientConductivityIdentity:
    """T064, T065: the gradient and the conductivity a row reports are
    identified by that row's own determination identifier, so two
    determinations measured over one shared interval keep their own
    rather than one updating the other's. Fails before: neither carries
    the determination's identifier at all (D16)."""

    def test_two_determinations_over_one_interval_keep_their_own_gradient_and_conductivity(
        self, db
    ):
        from heat_flow.models import IntervalConductivity, ThermalGradient

        header, rows = _corrected_header_and_rows()
        # rows[4] and rows[5] already share one site and depth range
        # (q_top=4490.00, q_bottom blank) in the real base fixture.
        dataset = _make_dataset(header, [rows[4], rows[5]])

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_errors() is False
        assert result.has_validation_errors() is False

        first_gradient = ThermalGradient.objects.get(local_id="R24-033563")
        second_gradient = ThermalGradient.objects.get(local_id="R24-053075")
        assert first_gradient != second_gradient
        assert float(first_gradient.value.magnitude) == 58.00
        assert float(second_gradient.value.magnitude) == 58.40

        first_conductivity = IntervalConductivity.objects.get(local_id="R24-033563")
        second_conductivity = IntervalConductivity.objects.get(local_id="R24-053075")
        assert first_conductivity != second_conductivity


class TestGHFDBReleaseImportResourceCorrectionsSuppliedOnly:
    """T066, T067: a row supplying some corrections and not others
    produces a correction record for each one supplied and none for the
    rest. Fails before: no correction record is created at all - the
    release reader does not yet build them (FR-029)."""

    def test_correction_records_exist_only_for_the_columns_the_row_supplies(self, db):
        from heat_flow.models import HeatFlow, HeatFlowCorrection

        header, rows = _corrected_header_and_rows()
        row = rows[4]
        for column in ("corr_S_flag", "corr_E_flag", "corr_HR_flag"):
            row = _with_cell(header, [row], 0, column, "")[0]
        dataset = _make_dataset(header, [row])

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_errors() is False
        assert result.has_validation_errors() is False

        determination = HeatFlow.objects.get()
        types = set(
            HeatFlowCorrection.objects.filter(heat_flow=determination).values_list(
                "correction_type", flat=True
            )
        )
        assert types == {"IS", "T", "TOPO", "PAL", "SUR", "CONV"}


class TestGHFDBReleaseImportResourceCorrectionFlagNormalization:
    """T068, T069: a correction flag that is bracketed, differently cased,
    or both is matched to its term rather than lost (FR-030). Fails
    before: it falls through to an unspecified value."""

    def test_a_differently_cased_correction_flag_is_read_as_its_term(self, db):
        from heat_flow.models import HeatFlow, HeatFlowCorrection

        header, rows = _corrected_header_and_rows()
        row = _with_cell(
            header, [rows[4]], 0, "corr_IS_flag", "  [TILT CORRECTED]  "
        )[0]
        dataset = _make_dataset(header, [row])

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_errors() is False
        assert result.has_validation_errors() is False

        determination = HeatFlow.objects.get()
        correction = HeatFlowCorrection.objects.get(
            heat_flow=determination, correction_type="IS"
        )
        assert correction.status == "tilt_corrected"


class TestGHFDBReleaseImportResourceProbeMetadata:
    """T070, T071: probe metadata is created once for an interval shared
    by several rows that supply it, and none is created for a row that
    supplies no probe columns. Fails before: it is created per row, or
    created empty (D18, FR-031)."""

    def test_probe_metadata_created_once_for_a_shared_interval_and_not_for_a_row_without_it(
        self, db
    ):
        from heat_flow.models import HeatFlowInterval, ProbeMetadata

        header, rows = _corrected_header_and_rows()
        # rows[4] shares one site and depth range with itself under a
        # second published determination identifier - the same interval,
        # both rows supplying identical probe columns.
        shared_first = rows[4]
        shared_second = _with_cell(header, [rows[4]], 0, "ID", "R24-999999")[0]
        # rows[3] belongs to a different site and supplies no probe
        # column at all.
        no_probe = rows[3]
        dataset = _make_dataset(header, [shared_first, shared_second, no_probe])

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_errors() is False
        assert result.has_validation_errors() is False

        assert ProbeMetadata.objects.count() == 1

        shared_interval = HeatFlowInterval.objects.get(site__local_id="R24-P003477")
        probe = ProbeMetadata.objects.get()
        assert probe.interval == shared_interval

        no_probe_interval = HeatFlowInterval.objects.get(site__local_id="R24-P004314")
        assert not ProbeMetadata.objects.filter(interval=no_probe_interval).exists()


class TestGHFDBReleaseImportResourceIntervalProbeDisagreement:
    """T072, T073: two rows sharing an interval but disagreeing about the
    probe that sampled it are refused, and the disagreement is reported.
    Fails before: the second row overwrites the first, or fails in a way
    that names nothing (D18, FR-035)."""

    def test_rows_disagreeing_about_a_shared_intervals_probe_are_both_refused(self, db):
        from heat_flow.models import ProbeMetadata

        header, rows = _corrected_header_and_rows()
        # rows[4] and rows[5] already share one site and depth range in
        # the real base fixture; giving row 4 a real, differing
        # probe_length makes them disagree about the probe rather than
        # one merely being silent about it.
        disagreeing_first = _with_cell(header, [rows[4]], 0, "probe_length", "10.00")[0]
        disagreeing_second = rows[5]
        dataset = _make_dataset(header, [disagreeing_first, disagreeing_second])

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_validation_errors() is True
        refused = {row.number: row for row in result.invalid_rows}
        assert {2, 3}.issubset(refused)
        for number in (2, 3):
            message = str(refused[number].error_dict["probe_length"][0])
            assert "10.00" in message
            assert "21.00" in message

        assert ProbeMetadata.objects.count() == 0


class TestGHFDBReleaseImportResourceMixedIntervals:
    """T063: a site with some rows giving a depth range and some giving
    none holds one interval for each distinct range plus the one
    indeterminate interval, and they are distinct records. Fails before:
    they are merged."""

    def test_site_holds_distinct_intervals_for_each_range_and_the_indeterminate_one(
        self, db
    ):
        from heat_flow.models import HeatFlowInterval

        header, rows = _corrected_header_and_rows()
        with_depth = _with_cell(header, [rows[4], rows[5]], 0, "q_bottom", "4520.00")
        with_depth = _with_cell(header, with_depth, 1, "q_bottom", "4520.00")
        no_depth = [rows[0], rows[1]]
        dataset = _make_dataset(header, with_depth + no_depth)

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_errors() is False
        assert result.has_validation_errors() is False

        assert HeatFlowInterval.objects.count() == 2
        with_depth_interval = HeatFlowInterval.objects.get(top__isnull=False)
        indeterminate_interval = HeatFlowInterval.objects.get(top__isnull=True)
        assert with_depth_interval != indeterminate_interval
        assert indeterminate_interval.bottom is None
