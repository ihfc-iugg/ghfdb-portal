# Tests for ``project/review/management/commands/repair_references.py``. The command runs on
# the table django-literature kept references in before 0.3, which each test creates inside its
# own transaction, so it is gone when the test ends.

import json
from io import StringIO

import pytest
from django.core.management import call_command
from django.db import connection
from literature.converters import from_csl_json
from review.management.commands.repair_references import LEGACY_TABLE

ARTICLE = {"type": "article-journal", "title": "Heat flow in the Baltic Shield"}


@pytest.fixture
def legacy_references(db):
    """Create the old reference table and return a function that stores a reference in it."""
    with connection.cursor() as cursor:
        cursor.execute(
            f"CREATE TABLE {LEGACY_TABLE}"
            " (id serial PRIMARY KEY, citation_key varchar(255), item jsonb)"
        )

    def store(key, **fields):
        item = {**ARTICLE, "id": key, **fields}
        with connection.cursor() as cursor:
            cursor.execute(
                f"INSERT INTO {LEGACY_TABLE} (citation_key, item) VALUES (%s, %s)",
                [key, json.dumps(item)],
            )
        return item

    return store


def stored(key):
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT item FROM {LEGACY_TABLE} WHERE citation_key = %s", [key]
        )
        (item,) = cursor.fetchone()
    return item if isinstance(item, dict) else json.loads(item)


def repair(*args):
    out = StringIO()
    call_command("repair_references", *args, stdout=out)
    return out.getvalue()


class TestRepairReferences:
    def test_an_issn_that_lost_its_leading_zeros_is_restored(self, legacy_references):
        legacy_references("Lister_1980", ISSN="948276")

        repair()

        assert stored("Lister_1980")["ISSN"] == "0094-8276"
        assert "note" not in stored("Lister_1980")

    def test_a_shortened_number_whose_check_digit_fails_is_kept_in_the_note(
        self, legacy_references
    ):
        legacy_references("Short_1990", ISSN="948277")

        repair()

        item = stored("Short_1990")
        assert "ISSN" not in item
        assert "948277" in item["note"]

    def test_an_isbn_filed_as_an_issn_moves_to_the_isbn(self, legacy_references):
        legacy_references("Zoth_1985", ISSN="978-3-510-96058-3")

        repair()

        item = stored("Zoth_1985")
        assert item["ISBN"] == "978-3-510-96058-3"
        assert "ISSN" not in item

    def test_an_issn_filed_as_an_isbn_moves_to_the_issn(self, legacy_references):
        legacy_references("Becker_1995", ISBN="0254-4903")

        repair()

        item = stored("Becker_1995")
        assert item["ISSN"] == "0254-4903"
        assert "ISBN" not in item

    def test_the_first_of_several_issns_is_kept_and_the_others_noted(
        self, legacy_references
    ):
        legacy_references(
            "Nature_2019", ISSN="0028-0836, 1476-4687", note="Cover story"
        )

        repair()

        item = stored("Nature_2019")
        assert item["ISSN"] == "0028-0836"
        assert item["note"].splitlines()[0] == "Cover story"
        assert "1476-4687" in item["note"]

    def test_pubmed_qualifiers_and_a_spaced_hyphen_leave_one_issn(
        self, legacy_references
    ):
        legacy_references("Birch_1947", ISSN="0012-821X (Print) 0012-821X (Linking)")
        legacy_references("Demetrescu_1973", ISSN="1220 - 5265")

        repair()

        assert stored("Birch_1947")["ISSN"] == "0012-821X"
        assert stored("Demetrescu_1973")["ISSN"] == "1220-5265"
        assert "note" not in stored("Birch_1947")
        assert "note" not in stored("Demetrescu_1973")

    def test_text_that_is_no_identifier_is_kept_in_the_note(self, legacy_references):
        legacy_references("He_2009", ISSN="J Asian Earth Sci")

        repair()

        item = stored("He_2009")
        assert "ISSN" not in item
        assert "J" in item["note"]
        assert "Sci" in item["note"]

    def test_a_doi_address_is_stored_as_the_doi(self, legacy_references):
        legacy_references("White_1969", DOI="https://doi.org/10.1029/JB074i022p05191")

        repair()

        assert stored("White_1969")["DOI"] == "10.1029/JB074i022p05191"

    def test_an_isbn_filed_as_a_doi_moves_to_the_isbn(self, legacy_references):
        legacy_references("Taylor_2015", DOI="978-1-74146-940-0")

        repair()

        item = stored("Taylor_2015")
        assert item["ISBN"] == "978-1-74146-940-0"
        assert "DOI" not in item

    def test_a_doi_that_is_no_doi_is_kept_in_the_note(self, legacy_references):
        legacy_references("Kaul_2003", DOI="10013/epic.16727")

        repair()

        item = stored("Kaul_2003")
        assert "DOI" not in item
        assert "10013/epic.16727" in item["note"]

    def test_a_number_too_long_to_store_is_kept_in_the_note(self, legacy_references):
        number = "Report " * 20
        legacy_references("Clement_1981", number=number)

        repair()

        item = stored("Clement_1981")
        assert "number" not in item
        assert number.strip() in item["note"]

    def test_a_reference_that_needs_nothing_is_left_as_it_was(self, legacy_references):
        before = legacy_references(
            "Pollack_1993", DOI="10.1029/93RG01249", ISSN="8755-1209"
        )

        repair()

        assert stored("Pollack_1993") == before

    def test_every_repaired_reference_can_be_converted(self, legacy_references):
        for key, fields in {
            "a": {"ISSN": "948276"},
            "b": {"ISSN": "0028-0836, 1476-4687", "ISBN": "0254-4903"},
            "c": {"DOI": "https://doi.org/10.1029/2023EA003186", "ISSN": "J Asian"},
            "d": {"number": "x" * 80},
        }.items():
            legacy_references(key, **fields)

        repair()

        for key in "abcd":
            from_csl_json(stored(key))

    def test_a_dry_run_writes_nothing(self, legacy_references):
        before = legacy_references("Lister_1980", ISSN="948276")

        out = repair("--dry-run")

        assert stored("Lister_1980") == before
        assert "0094-8276" in out

    def test_a_database_without_the_old_table_is_left_alone(self, db):
        repair()

        assert LEGACY_TABLE not in connection.introspection.table_names()
