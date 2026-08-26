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

from project.ghfdb.constants import CORRECTION_COL_MAP, MISSPELLED_COLUMNS, READ_COLUMNS
from project.ghfdb.resources.release import (
    GHFDBReleaseCSVFormat,
    GHFDBReleaseImportResource,
    _correction_status,
)
from project.ghfdb.resources.widgets import (
    ConceptWidget,
    MultiConceptWidget,
    YesNoWidget,
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
        row = _with_cell(header, [rows[4]], 0, "corr_IS_flag", "  [TILT CORRECTED]  ")[
            0
        ]
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


class TestGHFDBReleaseImportResourceSiteDisagreement:
    """T074, T075: two rows sharing a published site identifier but
    disagreeing about that site's own columns are refused, and the
    disagreement is reported. Fails before: one row's values win
    silently (FR-035)."""

    def test_rows_disagreeing_about_a_shared_sites_coordinates_are_both_refused(
        self, db
    ):
        from heat_flow.models import HeatFlowSite

        header, rows = _corrected_header_and_rows()
        # rows[0] and rows[4] already share the published site
        # identifier R24-P003477 in the real base fixture.
        disagreeing_first = rows[0]
        disagreeing_second = _with_cell(header, [rows[4]], 0, "lat_NS", "20.00000")[0]
        dataset = _make_dataset(header, [disagreeing_first, disagreeing_second])

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_validation_errors() is True
        refused = {row.number: row for row in result.invalid_rows}
        assert {2, 3}.issubset(refused)
        for number in (2, 3):
            message = str(refused[number].error_dict["lat_NS"][0])
            assert "16.10000" in message
            assert "20.00000" in message

        assert HeatFlowSite.objects.filter(local_id="R24-P003477").count() == 0


class TestGHFDBReleaseImportResourceExploPurposeDisagreement:
    """The `explo_purpose`-disagreement closure this run's brief adds to
    T074/T075: two rows sharing a published site identifier but
    disagreeing about `explo_purpose` are refused, the same sentence
    T074/T075 already deliver for the site's scalar columns. Fails
    before: `SITE_COLUMNS` omitted `explo_purpose`, so the disagreement
    imported clean. `explo_purpose` is many-valued, so the comparison is
    order-independent set equality, not string equality, and a blank
    column makes no statement (D24)."""

    def test_rows_disagreeing_about_explo_purpose_are_both_refused(self, db):
        from heat_flow.models import HeatFlowSite

        header, rows = _corrected_header_and_rows()
        # rows[0] and rows[4] already share the published site
        # identifier R24-P003477 in the real base fixture, both giving
        # explo_purpose "[Research]".
        disagreeing_first = rows[0]
        disagreeing_second = _with_cell(
            header, [rows[4]], 0, "explo_purpose", "[Mining]"
        )[0]
        dataset = _make_dataset(header, [disagreeing_first, disagreeing_second])

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_validation_errors() is True
        refused = {row.number: row for row in result.invalid_rows}
        assert {2, 3}.issubset(refused)
        for number in (2, 3):
            message = str(refused[number].error_dict["explo_purpose"][0])
            assert "research" in message
            assert "mining" in message

        assert HeatFlowSite.objects.filter(local_id="R24-P003477").count() == 0

    def test_the_same_purposes_in_a_different_order_do_not_disagree(self, db):
        from heat_flow.models import HeatFlowSite

        header, rows = _corrected_header_and_rows()
        agreeing_first = _with_cell(
            header, [rows[0]], 0, "explo_purpose", "[Research];[Mining]"
        )[0]
        agreeing_second = _with_cell(
            header, [rows[4]], 0, "explo_purpose", "[Mining];[Research]"
        )[0]
        dataset = _make_dataset(header, [agreeing_first, agreeing_second])

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_errors() is False
        assert result.has_validation_errors() is False
        assert HeatFlowSite.objects.filter(local_id="R24-P003477").count() == 1


class TestGHFDBReleaseImportResourceAbsentValueMarker:
    """T076, T077: a cell holding the published absent-value marker is
    read as no value, and creates no record the row did not describe.
    Fails before: it is refused as a non-numeric value in a numeric
    column (FR-012). Row 3 of the real base fixture carries the marker
    by design (T004), in ``q_top``, ``q_bottom``, ``T_grad_mean`` and
    ``tc_mean`` among others."""

    def test_the_absent_value_marker_is_read_as_no_value(self, db):
        from heat_flow.models import (
            HeatFlow,
            HeatFlowInterval,
            IntervalConductivity,
            ThermalGradient,
        )

        header, rows = _corrected_header_and_rows()
        dataset = _make_dataset(header, [rows[3]])

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_errors() is False
        assert result.has_validation_errors() is False

        determination = HeatFlow.objects.get()
        assert float(determination.value.magnitude) == 67.0

        interval = HeatFlowInterval.objects.get()
        assert interval.top is None
        assert interval.bottom is None

        assert ThermalGradient.objects.count() == 0
        assert IntervalConductivity.objects.count() == 0


class TestGHFDBReleaseImportResourceManyValuedVocabularyRefusal:
    """T081, T082: a vocabulary value matching no term in a column holding
    several values is refused and reported, the same as a single-valued
    column already is (T080). Fails before: the failure is caught inside
    ``RelatedModelWidget.set_m2m_relations`` and discarded, so the row
    imports with the relation left empty (D11)."""

    def test_an_unrecognised_lithology_term_is_refused(self, db):
        from heat_flow.models import HeatFlowInterval

        header, rows = _corrected_header_and_rows()
        row = _with_cell(header, [rows[4]], 0, "geo_lithology", "not_a_real_lithology")[
            0
        ]
        dataset = _make_dataset(header, [row])

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_validation_errors() is True
        error_dict = result.invalid_rows[0].error_dict
        assert "geo_lithology" in error_dict
        message = str(error_dict["geo_lithology"][0])
        assert "not_a_real_lithology" in message

        assert HeatFlowInterval.objects.count() == 0


class TestGHFDBReleaseImportResourceScalarRefusalNamesTheColumn:
    """T083, T084: a value a related record's own scalar columns refuse -
    a numeric-looking value in a column holding a controlled-vocabulary
    label, or free text in a column holding a quantity - is refused with
    that column and the value named. Fails before:
    ``RelatedModelWidget.clean`` re-raises naming only the model class
    (e.g. 'HeatFlowSite: ...'), so the published column a curator would
    look for in the header never appears in the message."""

    def test_an_unmatched_environment_value_names_the_column(self, db):
        from heat_flow.models import HeatFlowSite

        header, rows = _corrected_header_and_rows()
        row = _with_cell(header, [rows[4]], 0, "environment", "9999")[0]
        dataset = _make_dataset(header, [row])

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_validation_errors() is True
        error_dict = result.invalid_rows[0].error_dict
        assert "environment" in error_dict
        message = str(error_dict["environment"][0])
        assert "9999" in message

        assert HeatFlowSite.objects.count() == 0

    def test_text_in_a_quantity_column_names_the_column(self, db):
        from heat_flow.models import HeatFlowSite

        header, rows = _corrected_header_and_rows()
        row = _with_cell(header, [rows[4]], 0, "elevation", "not-a-number")[0]
        dataset = _make_dataset(header, [row])

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_validation_errors() is True
        error_dict = result.invalid_rows[0].error_dict
        assert "elevation" in error_dict
        message = str(error_dict["elevation"][0])
        assert "not-a-number" in message

        assert HeatFlowSite.objects.count() == 0


class TestGHFDBReleaseImportResourceSiteNameStoredAsGiven:
    """T085, T086, T087: a site's name is a label, not a key - stored
    exactly as the file gives it, including a numeric or placeholder
    value, and never causes a refusal (D14, FR-032). A site's location
    is set from its coordinates regardless of what its name is (D14).
    Fails before: a numeric name is refused as a non-text value, and an
    empty name produces a site with no location."""

    def test_a_numeric_name_imports_and_is_stored_verbatim(self, db):
        from heat_flow.models import HeatFlowSite

        header, rows = _corrected_header_and_rows()
        row = _with_cell(header, [rows[4]], 0, "name", "12345")[0]
        dataset = _make_dataset(header, [row])

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_errors() is False
        assert result.has_validation_errors() is False

        site = HeatFlowSite.objects.get()
        assert site.name == "12345"
        assert site.location is not None

    def test_a_placeholder_name_imports_and_the_site_still_gets_a_location(self, db):
        from heat_flow.models import HeatFlowSite

        header, rows = _corrected_header_and_rows()
        row = _with_cell(header, [rows[4]], 0, "name", "?")[0]
        dataset = _make_dataset(header, [row])

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_errors() is False
        assert result.has_validation_errors() is False

        site = HeatFlowSite.objects.get()
        assert site.name == "?"
        assert site.location is not None

    def test_an_empty_name_imports_and_the_site_still_gets_a_location(self, db):
        from heat_flow.models import HeatFlowSite

        header, rows = _corrected_header_and_rows()
        row = _with_cell(header, [rows[4]], 0, "name", "")[0]
        dataset = _make_dataset(header, [row])

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_errors() is False
        assert result.has_validation_errors() is False

        site = HeatFlowSite.objects.get()
        assert site.name == ""
        assert site.location is not None


class TestGHFDBReleaseImportResourceSuppliedQualityCodeDiscarded:
    """T088, T089: a row carrying a supplied quality code imports, and
    that code is not stored anywhere - the portal computes quality from
    what it holds and never ingests a supplied one (D13, FR-033). Fails
    before: it is stored. Row 4 of the real base fixture carries a real
    ``Quality_Code`` value by design (R1)."""

    def test_the_supplied_quality_code_is_not_stored(self, db):
        from heat_flow.models import HeatFlow, ParentHeatFlow

        header, rows = _corrected_header_and_rows()
        assert rows[4][header.index("Quality_Code")] == "U2.M3.s-----r"
        dataset = _make_dataset(header, [rows[4]])

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_errors() is False
        assert result.has_validation_errors() is False

        determination = HeatFlow.objects.get()
        assert determination.quality != "U2.M3.s-----r"
        parent = ParentHeatFlow.objects.get()
        assert parent.quality != "U2.M3.s-----r"


class TestGHFDBReleaseImportResourceAssessmentColumnsRecognizedAndDiscarded:
    """T090, T091: a file carrying the assessment team's own columns is
    not refused for carrying them, and their values are not stored
    anywhere - recording assessment in the portal is aspirational and no
    field waits for them (D13, FR-034). Fails before: the columns are
    refused as undefined. Row 4 of the real base fixture carries real
    values for all four columns."""

    def test_the_assessment_columns_do_not_refuse_the_file_and_are_not_stored(self, db):
        from heat_flow.models import HeatFlow, ParentHeatFlow

        header, rows = _corrected_header_and_rows()
        assert rows[4][header.index("Reviewer_name")] == "Florian Neumann"
        dataset = _make_dataset(header, [rows[4]])

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_errors() is False
        assert result.has_validation_errors() is False

        determination = HeatFlow.objects.get()
        parent = ParentHeatFlow.objects.get()
        assert determination.c_comment != "Florian Neumann"
        assert parent.comment != "Florian Neumann"


class TestGHFDBReleaseImportResourceRowCountGuarantee:
    """T092, T093: a file of n valid rows produces n determinations - no
    row is dropped on the way in, whether or not it shares a site or an
    interval with another (D14, FR-015). Every row is read, or reported
    as refused, and nothing else. Fails before: rows sharing a site are
    removed from the file as it is read, with no count and no notice."""

    def test_n_valid_rows_produce_n_determinations(self, db):
        from heat_flow.models import HeatFlow

        header, rows = _corrected_header_and_rows()
        dataset = _make_dataset(header, rows)

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_errors() is False
        assert result.has_validation_errors() is False
        assert result.total_rows == len(rows)
        assert HeatFlow.objects.count() == len(rows)


class TestGHFDBReleaseImportResourceRemainingColumnsReachTheirFields:
    """The columns T115's own mapping test needs wired: ``p_comment`` and
    ``corr_HP_flag`` on the parent, ``c_comment``, ``expedition``,
    ``water_temperature``, ``q_date``, ``q_method`` and ``relevant_child``
    on the determination. Each already has a field on the model - the
    sibling contributor-template resource (parent.py, child.py) reaches
    every one of them - but this resource does not yet read any of them.
    Row 4 of the real base fixture carries a real value for all eight."""

    def test_the_eight_columns_land_in_their_fields(self, db):
        from heat_flow.models import HeatFlow, ParentHeatFlow

        header, rows = _corrected_header_and_rows()
        row = _with_cell(header, [rows[4]], 0, "p_comment", "some comment")[0]
        row = _with_cell(header, [row], 0, "c_comment", "some other comment")[0]
        row = _with_cell(header, [row], 0, "water_temperature", "4.5")[0]
        dataset = _make_dataset(header, [row])

        resource = GHFDBReleaseImportResource()
        result = resource.import_data(dataset, dry_run=False, raise_errors=False)

        assert result.has_errors() is False
        assert result.has_validation_errors() is False

        parent = ParentHeatFlow.objects.get()
        assert parent.comment == "some comment"
        assert parent.corr_HP_flag is False

        determination = HeatFlow.objects.get()
        assert determination.c_comment == "some other comment"
        assert determination.expedition == "R.V Vema cruise 19"
        assert float(determination.water_temperature.magnitude) == 4.5
        assert str(determination.date_acquired) == "1963-02"
        assert determination.is_relevant is False
        assert {m.label for m in determination.method.all()} == {"Interval method"}


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


def _fully_populated_row():
    """Row 4 of the real base fixture, with a real value filled in by hand
    for every column that row leaves blank or ``[unspecified]`` (T115) -
    every ``READ_COLUMNS`` entry gets something real to assert against, not
    an absence that would prove nothing about where a value lands."""
    header, rows = _corrected_header_and_rows()
    row = list(rows[4])
    overrides = {
        "Country": "Some Country",
        "T_grad_mean_cor": "60.00",
        "T_grad_uncertainty": "2.0",
        "T_grad_uncertainty_cor": "2.5",
        "T_shutin_bottom": "5",
        "T_shutin_top": "3",
        "T_method_top": "[BHT]",
        "T_method_bottom": "[BHT]",
        "T_corr_top": "[Horner plot]",
        "T_corr_bottom": "[Horner plot]",
        "c_comment": "child comment text",
        "probe_length": "12.5",
        "probe_penetration": "3.5",
        "probe_tilt": "2.0",
        "p_comment": "parent comment text",
        "q_bottom": "4520.00",
        "tc_number": "5",
        "tc_uncertainty": "0.05",
        "tc_pT_function": "[Other]",
        "total_depth_MD": "5000.00",
        "total_depth_TVD": "4800.00",
        "water_temperature": "4.5",
    }
    for column, value in overrides.items():
        row = _with_cell(header, [row], 0, column, value)[0]
    return header, row


def _import_fully_populated_row():
    """Import ``_fully_populated_row`` and return every record it produces,
    keyed by the object a column's assertion needs, plus the row itself
    (as a dict) for the assertion to read its own expected value from."""
    from heat_flow.models import (
        HeatFlow,
        HeatFlowCorrection,
        HeatFlowInterval,
        HeatFlowSite,
        IntervalConductivity,
        ParentHeatFlow,
        ProbeMetadata,
        ThermalGradient,
    )

    header, row = _fully_populated_row()
    dataset = _make_dataset(header, [row])

    resource = GHFDBReleaseImportResource()
    result = resource.import_data(dataset, dry_run=False, raise_errors=False)
    assert result.has_errors() is False
    assert result.has_validation_errors() is False

    determination = HeatFlow.objects.get()
    return {
        "row": dict(zip(header, row, strict=True)),
        "determination": determination,
        "parent": ParentHeatFlow.objects.get(),
        "site": HeatFlowSite.objects.get(),
        "interval": HeatFlowInterval.objects.get(),
        "gradient": ThermalGradient.objects.get(),
        "conductivity": IntervalConductivity.objects.get(),
        "probe": ProbeMetadata.objects.get(),
        "corrections": {
            c.correction_type: c
            for c in HeatFlowCorrection.objects.filter(heat_flow=determination)
        },
    }


def _quantity_matches(quantity, raw):
    return quantity is not None and float(quantity.magnitude) == float(raw)


def _concept_key_matches(vocabulary):
    def check(actual, raw):
        expected = ConceptWidget(vocabulary=vocabulary).clean(raw, row={})
        return str(actual) == expected

    return check


def _concept_set_matches(vocabulary):
    def check(manager, raw):
        expected = {str(c) for c in MultiConceptWidget(vocabulary).clean(raw, row={})}
        return {str(c) for c in manager.all()} == expected

    return check


def _correction_matches(column):
    def check(o, raw):
        correction_type = CORRECTION_COL_MAP[column]
        return o["corrections"][correction_type].status == _correction_status(raw)

    return check


def _heat_flow_method_vocabulary():
    from heat_flow import vocabularies

    return vocabularies.HeatFlowMethod


def _exploration_purpose_vocabulary():
    from heat_flow import vocabularies

    return vocabularies.ExplorationPurpose


def _simple_lithology_vocabulary():
    from fairdm_geo.vocabularies.cgi.geosciml import SimpleLithology

    return SimpleLithology


def _geological_timescale_vocabulary():
    from fairdm_geo.vocabularies.stratigraphy import GeologicalTimescale

    return GeologicalTimescale


def _temperature_method_vocabulary():
    from heat_flow import vocabularies

    return vocabularies.TemperatureMethod


def _temperature_correction_vocabulary():
    from heat_flow import vocabularies

    return vocabularies.TemperatureCorrection


def _conductivity_vocabulary(name):
    def get():
        from heat_flow import vocabularies

        return getattr(vocabularies, name)

    return get


def _probe_type_vocabulary():
    from heat_flow import vocabularies

    return vocabularies.ProbeType


# T115, SC-007: one assertion per ``READ_COLUMNS`` entry, each a
# ``(objects, raw) -> bool`` check reading the object(s)
# ``_import_fully_populated_row`` returns and the row's own raw value for
# that column. A column landing nowhere, or in the wrong field, fails its
# own check rather than an aggregate one; a column added to
# ``READ_COLUMNS`` with no matching key here fails
# ``test_every_read_column_has_an_assertion`` by name.
COLUMN_ASSERTIONS = {
    # -- site --
    "name": lambda o, raw: o["site"].name == raw,
    "lat_NS": lambda o, raw: abs(float(o["site"].location.y) - float(raw)) < 1e-6,
    "long_EW": lambda o, raw: abs(float(o["site"].location.x) - float(raw)) < 1e-6,
    "elevation": lambda o, raw: _quantity_matches(o["site"].elevation, raw),
    "environment": lambda o, raw: _concept_key_matches(
        _heat_flow_environment_vocabulary()
    )(o["site"].environment, raw),
    "explo_method": lambda o, raw: _concept_key_matches(
        _exploration_method_vocabulary()
    )(o["site"].explo_method, raw),
    "explo_purpose": lambda o, raw: _concept_set_matches(
        _exploration_purpose_vocabulary()
    )(o["site"].explo_purpose, raw),
    "total_depth_MD": lambda o, raw: _quantity_matches(o["site"].length, raw),
    "total_depth_TVD": lambda o, raw: _quantity_matches(o["site"].vertical_depth, raw),
    "Country": lambda o, raw: o["site"].country == raw,
    "Region": lambda o, raw: o["site"].region == raw,
    "Continent": lambda o, raw: o["site"].continent == raw,
    "Domain": lambda o, raw: o["site"].domain == raw,
    "ID_parent": lambda o, raw: o["site"].local_id == raw,
    # -- parent --
    "q": lambda o, raw: _quantity_matches(o["parent"].value, raw),
    "q_uncertainty": lambda o, raw: _quantity_matches(o["parent"].uncertainty, raw),
    "p_comment": lambda o, raw: o["parent"].comment == raw,
    "corr_HP_flag": lambda o, raw: o["parent"].corr_HP_flag == YesNoWidget().clean(raw),
    # -- determination --
    "ID": lambda o, raw: o["determination"].local_id == raw,
    "qc": lambda o, raw: _quantity_matches(o["determination"].value, raw),
    "qc_uncertainty": lambda o, raw: _quantity_matches(
        o["determination"].uncertainty, raw
    ),
    "c_comment": lambda o, raw: o["determination"].c_comment == raw,
    "expedition": lambda o, raw: o["determination"].expedition == raw,
    "water_temperature": lambda o, raw: _quantity_matches(
        o["determination"].water_temperature, raw
    ),
    "q_date": lambda o, raw: str(o["determination"].date_acquired) == raw,
    "q_method": lambda o, raw: _concept_set_matches(_heat_flow_method_vocabulary())(
        o["determination"].method, raw
    ),
    "relevant_child": lambda o, raw: (
        o["determination"].is_relevant == (YesNoWidget().clean(raw) or False)
    ),
    "publication_reference": lambda o, raw: (
        o["determination"].dataset.reference.citation_key == raw
    ),
    # -- interval --
    "q_top": lambda o, raw: _quantity_matches(o["interval"].top, raw),
    "q_bottom": lambda o, raw: _quantity_matches(o["interval"].bottom, raw),
    "geo_lithology": lambda o, raw: _concept_set_matches(
        _simple_lithology_vocabulary()
    )(o["interval"].lithology, raw),
    "geo_stratigraphy": lambda o, raw: _concept_set_matches(
        _geological_timescale_vocabulary()
    )(o["interval"].age, raw),
    # -- gradient --
    "T_grad_mean": lambda o, raw: _quantity_matches(o["gradient"].value, raw),
    "T_grad_uncertainty": lambda o, raw: _quantity_matches(
        o["gradient"].uncertainty, raw
    ),
    "T_grad_mean_cor": lambda o, raw: _quantity_matches(
        o["gradient"].corrected_value, raw
    ),
    "T_grad_uncertainty_cor": lambda o, raw: _quantity_matches(
        o["gradient"].corrected_uncertainty, raw
    ),
    "T_shutin_top": lambda o, raw: _quantity_matches(o["gradient"].shutin_top, raw),
    "T_shutin_bottom": lambda o, raw: _quantity_matches(
        o["gradient"].shutin_bottom, raw
    ),
    "T_number": lambda o, raw: o["gradient"].number == int(raw),
    "T_method_top": lambda o, raw: _concept_set_matches(
        _temperature_method_vocabulary()
    )(o["gradient"].method_top, raw),
    "T_method_bottom": lambda o, raw: _concept_set_matches(
        _temperature_method_vocabulary()
    )(o["gradient"].method_bottom, raw),
    "T_corr_top": lambda o, raw: _concept_set_matches(
        _temperature_correction_vocabulary()
    )(o["gradient"].correction_top, raw),
    "T_corr_bottom": lambda o, raw: _concept_set_matches(
        _temperature_correction_vocabulary()
    )(o["gradient"].correction_bottom, raw),
    # -- conductivity --
    "tc_mean": lambda o, raw: _quantity_matches(o["conductivity"].value, raw),
    "tc_uncertainty": lambda o, raw: _quantity_matches(
        o["conductivity"].uncertainty, raw
    ),
    "tc_number": lambda o, raw: o["conductivity"].number == int(raw),
    "tc_source": lambda o, raw: _concept_set_matches(
        _conductivity_vocabulary("ConductivitySource")()
    )(o["conductivity"].source, raw),
    "tc_location": lambda o, raw: _concept_set_matches(
        _conductivity_vocabulary("ConductivityLocation")()
    )(o["conductivity"].location, raw),
    "tc_method": lambda o, raw: _concept_set_matches(
        _conductivity_vocabulary("ConductivityMethod")()
    )(o["conductivity"].method, raw),
    "tc_saturation": lambda o, raw: _concept_set_matches(
        _conductivity_vocabulary("ConductivitySaturation")()
    )(o["conductivity"].saturation, raw),
    "tc_pT_conditions": lambda o, raw: _concept_set_matches(
        _conductivity_vocabulary("ConductivityPTConditions")()
    )(o["conductivity"].pT_conditions, raw),
    "tc_pT_function": lambda o, raw: _concept_set_matches(
        _conductivity_vocabulary("ConductivityPTFunction")()
    )(o["conductivity"].pT_function, raw),
    "tc_strategy": lambda o, raw: _concept_set_matches(
        _conductivity_vocabulary("ConductivityStrategy")()
    )(o["conductivity"].strategy, raw),
    # -- probe metadata --
    "probe_penetration": lambda o, raw: _quantity_matches(o["probe"].penetration, raw),
    "probe_length": lambda o, raw: _quantity_matches(o["probe"].length, raw),
    "probe_tilt": lambda o, raw: _quantity_matches(o["probe"].tilt, raw),
    "probe_type": lambda o, raw: _concept_set_matches(_probe_type_vocabulary())(
        o["probe"].probe_type, raw
    ),
    # -- corrections --
    **{column: _correction_matches(column) for column in CORRECTION_COL_MAP},
}


def _heat_flow_environment_vocabulary():
    from heat_flow import vocabularies

    return vocabularies.GeographicEnvironment


def _exploration_method_vocabulary():
    from heat_flow import vocabularies

    return vocabularies.ExplorationMethod


class TestGHFDBReleaseImportResourceColumnMapping:
    """T115: every column the definition (``READ_COLUMNS``) marks as read
    lands in the field that holds it, asserted column by column - not in
    aggregate - against one fully populated row, and failing for any read
    column that carries no assertion here rather than being dropped in
    silence (SC-007). Fails before: the mapping was asserted only in
    aggregate (a handful of fields on the story's own spine test), so a
    column could go nowhere unnoticed."""

    def test_every_read_column_has_an_assertion(self):
        assert set(COLUMN_ASSERTIONS) == READ_COLUMNS

    @pytest.mark.parametrize("column", sorted(READ_COLUMNS))
    def test_column_lands_in_its_field(self, db, column):
        objects = _import_fully_populated_row()
        assertion = COLUMN_ASSERTIONS.get(column)
        assert assertion is not None, (
            f"{column!r} is a read column with no assertion registered"
        )
        raw = objects["row"][column]
        assert assertion(objects, raw), (
            f"{column!r}: {raw!r} did not land in its field as expected"
        )


class TestGHFDBReleaseImportResourceReimportRecordCounts:
    """T097: importing an unchanged file twice leaves every record count
    identical to after the first import. Fails before: the second import
    doubles what the portal holds - an interval's identity (D15, T059,
    T060) is kept only in a per-pass dictionary (D23), so a second pass
    builds a second set of intervals, and everything measured over them,
    again."""

    def test_reimporting_an_unchanged_file_leaves_every_count_identical(self, db):
        from heat_flow.models import (
            HeatFlow,
            HeatFlowCorrection,
            HeatFlowInterval,
            HeatFlowSite,
            IntervalConductivity,
            ParentHeatFlow,
            ProbeMetadata,
            ThermalGradient,
        )

        models = (
            HeatFlowSite,
            ParentHeatFlow,
            HeatFlowInterval,
            HeatFlow,
            ThermalGradient,
            IntervalConductivity,
            HeatFlowCorrection,
            ProbeMetadata,
        )

        def counts():
            return {model.__name__: model.objects.count() for model in models}

        header, rows = _corrected_header_and_rows()

        first_result = GHFDBReleaseImportResource().import_data(
            _make_dataset(header, rows), dry_run=False, raise_errors=False
        )
        assert first_result.has_errors() is False
        assert first_result.has_validation_errors() is False
        counts_after_first = counts()
        assert counts_after_first["HeatFlow"] == len(rows)

        second_result = GHFDBReleaseImportResource().import_data(
            _make_dataset(header, rows), dry_run=False, raise_errors=False
        )

        assert second_result.has_errors() is False
        assert second_result.has_validation_errors() is False
        assert counts() == counts_after_first


class TestGHFDBReleaseImportResourceReimportRecordValues:
    """T098: importing an unchanged file twice leaves every stored value
    identical too, not merely the counts. Counts can match while values
    have been overwritten with something else."""

    def test_reimporting_an_unchanged_file_leaves_every_stored_value_identical(
        self, db
    ):
        from heat_flow.models import (
            HeatFlow,
            HeatFlowSite,
            IntervalConductivity,
            ParentHeatFlow,
            ThermalGradient,
        )

        def snapshot():
            site = HeatFlowSite.objects.get(local_id="R24-P003477")
            parent = ParentHeatFlow.objects.get(local_id="R24-P003477")
            determination = HeatFlow.objects.get(local_id="R24-033563")
            gradient = ThermalGradient.objects.get(local_id="R24-033563")
            conductivity = IntervalConductivity.objects.get(local_id="R24-033563")
            return {
                "site_name": site.name,
                "parent_value": float(parent.value.magnitude),
                "determination_value": float(determination.value.magnitude),
                "gradient_value": float(gradient.value.magnitude),
                "conductivity_value": float(conductivity.value.magnitude),
            }

        header, rows = _corrected_header_and_rows()

        first_result = GHFDBReleaseImportResource().import_data(
            _make_dataset(header, rows), dry_run=False, raise_errors=False
        )
        assert first_result.has_errors() is False
        values_after_first = snapshot()

        second_result = GHFDBReleaseImportResource().import_data(
            _make_dataset(header, rows), dry_run=False, raise_errors=False
        )

        assert second_result.has_errors() is False
        assert second_result.has_validation_errors() is False
        assert snapshot() == values_after_first


class TestGHFDBReleaseImportResourceReimportCorrectedValue:
    """T099, T100: correcting one value and re-importing updates that
    record and creates no second one - proving a determination is found
    by its published determination identifier (D10) rather than created
    again. Fails before: a second record is created."""

    def test_correcting_a_value_and_reimporting_updates_the_record(self, db):
        from heat_flow.models import HeatFlow

        header, rows = _corrected_header_and_rows()
        row = rows[4]

        first_result = GHFDBReleaseImportResource().import_data(
            _make_dataset(header, [row]), dry_run=False, raise_errors=False
        )
        assert first_result.has_errors() is False
        determination = HeatFlow.objects.get(local_id="R24-033563")
        assert float(determination.value.magnitude) == 48.0

        corrected_row = _with_cell(header, [row], 0, "qc", "55.00")[0]
        second_result = GHFDBReleaseImportResource().import_data(
            _make_dataset(header, [corrected_row]), dry_run=False, raise_errors=False
        )

        assert second_result.has_errors() is False
        assert second_result.has_validation_errors() is False
        assert HeatFlow.objects.filter(local_id="R24-033563").count() == 1
        determination.refresh_from_db()
        assert float(determination.value.magnitude) == 55.0


class TestGHFDBReleaseImportResourceReimportGradientConductivity:
    """T101: re-importing finds the gradient and the conductivity a
    determination was derived from, rather than creating a second pair
    (D16 - both take the determination's own identifier). Fails before:
    a second pair is created on every import."""

    def test_reimporting_finds_the_gradient_and_conductivity_rather_than_duplicating(
        self, db
    ):
        from heat_flow.models import IntervalConductivity, ThermalGradient

        header, rows = _corrected_header_and_rows()
        row = rows[4]

        first_result = GHFDBReleaseImportResource().import_data(
            _make_dataset(header, [row]), dry_run=False, raise_errors=False
        )
        assert first_result.has_errors() is False
        assert ThermalGradient.objects.filter(local_id="R24-033563").count() == 1
        assert IntervalConductivity.objects.filter(local_id="R24-033563").count() == 1

        second_result = GHFDBReleaseImportResource().import_data(
            _make_dataset(header, [row]), dry_run=False, raise_errors=False
        )

        assert second_result.has_errors() is False
        assert second_result.has_validation_errors() is False
        assert ThermalGradient.objects.filter(local_id="R24-033563").count() == 1
        assert IntervalConductivity.objects.filter(local_id="R24-033563").count() == 1


class TestGHFDBReleaseImportResourceReimportCorrections:
    """T102: re-importing finds each correction by its determination and
    its correction type, rather than creating a second record of the
    same type (R7 - the model's own ``unique_together``). Fails before:
    duplicates accumulate."""

    def test_reimporting_finds_corrections_rather_than_duplicating(self, db):
        from heat_flow.models import HeatFlow, HeatFlowCorrection

        header, rows = _corrected_header_and_rows()
        row = rows[4]

        first_result = GHFDBReleaseImportResource().import_data(
            _make_dataset(header, [row]), dry_run=False, raise_errors=False
        )
        assert first_result.has_errors() is False
        determination = HeatFlow.objects.get(local_id="R24-033563")
        first_count = HeatFlowCorrection.objects.filter(heat_flow=determination).count()
        assert first_count > 0

        second_result = GHFDBReleaseImportResource().import_data(
            _make_dataset(header, [row]), dry_run=False, raise_errors=False
        )

        assert second_result.has_errors() is False
        assert (
            HeatFlowCorrection.objects.filter(heat_flow=determination).count()
            == first_count
        )

