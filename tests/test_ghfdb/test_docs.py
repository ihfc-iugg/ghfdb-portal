"""The published-structure page has to name the query surface it documents.

T121. A page that falls behind the code is worse than no page, so the names it
promises are checked against the module rather than trusted.
"""

import pathlib

import pytest

pytestmark = pytest.mark.ghfdb

PAGE = pathlib.Path(__file__).parents[2] / "docs" / "data_models" / "published-structure.md"


class TestPublishedStructurePage:
    def test_the_page_exists_and_is_in_the_navigation(self):
        assert PAGE.exists()
        index = (PAGE.parent / "index.md").read_text()
        assert "published-structure" in index

    def test_it_names_every_public_queryset_method_this_feature_defines(self):
        """Read from the modules, so a method added or renamed without a
        documentation change fails here."""
        import inspect

        from project.ghfdb.managers import GHFDBChildQuerySet, GHFDBParentQuerySet

        page = PAGE.read_text()
        for queryset in (GHFDBChildQuerySet, GHFDBParentQuerySet):
            for name, member in inspect.getmembers(queryset, inspect.isfunction):
                if name.startswith("_") or member.__module__ != queryset.__module__:
                    continue
                assert f"{name}()" in page, f"{queryset.__name__}.{name}() undocumented"

    def test_it_names_the_two_corrected_column_spellings(self):
        """The page is where a curator finds out why the header they know is
        not the header they see."""
        page = PAGE.read_text()
        for corrected in ("tc_pT_function", "Ref_IGSN"):
            assert corrected in page

    def test_it_names_the_columns_that_are_always_empty(self):
        page = PAGE.read_text()
        for empty in ("Ref_IGSN", "publication_reference", "data_reference"):
            assert empty in page
