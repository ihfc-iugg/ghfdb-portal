# Tests for the published-column mapping (``project/ghfdb/columns.py``). FS-002.

import pytest
from django.contrib.admin.utils import label_for_field

from project.ghfdb.columns import ColumnDisplay, PublishedColumns
from project.ghfdb.constants import CHILD_COLUMNS, PARENT_COLUMNS

pytestmark = pytest.mark.ghfdb


class TestPublishedColumns:
    # The mapping from a published column name to how its value is reached, and the
    # builder that turns a canonical column list into display callables (R1).

    def test_every_published_column_has_an_entry(self):
        missing = [
            name
            for name in CHILD_COLUMNS + PARENT_COLUMNS
            if name not in PublishedColumns.ENTRIES
        ]
        assert missing == []

    def test_a_column_the_map_does_not_cover_is_refused_and_named(self):
        # FS-002 SC-007: the gate is proven against the defect it exists to catch, not
        # only against the passing case.
        with pytest.raises(ValueError) as excinfo:
            ColumnDisplay.list_display_for([*CHILD_COLUMNS, "q_unmapped"])

        assert "q_unmapped" in str(excinfo.value)

    def test_each_heading_is_the_published_name_verbatim(self):
        for name in CHILD_COLUMNS + PARENT_COLUMNS:
            assert ColumnDisplay.build(name).short_description == name

        for corrected in (
            "tc_pT_function",
            "Ref_IGSN",
            "quality_child",
            "quality_parent",
        ):
            assert corrected in PublishedColumns.ENTRIES
            assert ColumnDisplay.build(corrected).short_description == corrected

        for superseded in ("tc_pT_fuction", "Ref_ISGN", "quality"):
            assert superseded not in PublishedColumns.ENTRIES

    def test_an_annotation_column_reads_the_annotation_off_the_row(self):

        class Row:
            qc = 42.0

        assert ColumnDisplay.build("qc")(Row()) == 42.0

    def test_quality_child_and_quality_parent_each_read_their_own_annotation(self):
        # Revised under F12: ``quality_child`` and ``quality_parent`` both trace
        # back to the one ``quality`` field.

        class Row:
            quality_child = "AAAA"
            quality_parent = "BBBB"

        child_display = ColumnDisplay.build("quality_child")
        parent_display = ColumnDisplay.build("quality_parent")

        assert child_display(Row()) == "AAAA"
        assert child_display.short_description == "quality_child"
        assert parent_display(Row()) == "BBBB"
        assert parent_display.short_description == "quality_parent"

    @pytest.mark.django_db
    def test_a_many_valued_column_joins_its_labels_and_issues_no_query_when_prefetched(
        self, django_assert_num_queries, sites_by_contribution
    ):
        # FS-002 R1 group three, and the N+1 this feature exists to avoid.
        from project.ghfdb.models import GHFDBParent

        site = sites_by_contribution["all_contributing"]
        purposes = list(site.sample.explo_purpose.all())
        assert len(purposes) == 2
        expected = "; ".join(str(purpose) for purpose in purposes)

        row = GHFDBParent.objects.as_ghfdb_flat().with_children().get(pk=site.pk)

        with django_assert_num_queries(0):
            members = list(row.sample.heatflowsite.explo_purpose.all())
        assert len(members) == 2

        display = ColumnDisplay.build("explo_purpose")
        assert display(row) == expected

    def test_a_many_valued_column_renders_empty_when_the_path_breaks(self):
        # A missing relationship anywhere along the path renders empty rather than
        # raising, which is FS-002 FR-006 applied to the changelist.

        class Row:
            thermal_gradient = None

        assert ColumnDisplay.build("T_method_top")(Row()) == ""

    def test_the_columns_nothing_resolves_read_the_annotation_managers_py_sets(self):
        # Revised under F12: ``publication_reference`` and ``data_reference`` are
        # present and empty by decision (FS-002), but that decision is made once.

        class Row:
            publication_reference = ""
            data_reference = ""

        for name in ("publication_reference", "data_reference"):
            assert ColumnDisplay.build(name)(Row()) == ""

    def test_ref_igsn_reads_whatever_the_row_carries(self):
        # ``Ref_IGSN`` is a real accessor onto the interval's sample identifier now,
        # read like any other scalar column — empty when the row's annotation is empty,
        # and the stored value when it is not.

        class EmptyRow:
            Ref_IGSN = ""

        class PopulatedRow:
            Ref_IGSN = "10.60516/AU1101"

        display = ColumnDisplay.build("Ref_IGSN")
        assert display(EmptyRow()) == ""
        assert display(PopulatedRow()) == "10.60516/AU1101"

    def test_headings_are_the_canonical_order(self):
        # The headings the built tuple produces equal the order ``constants.py`` gives.
        for columns in (CHILD_COLUMNS, PARENT_COLUMNS):
            built = ColumnDisplay.list_display_for(columns)
            assert [display.short_description for display in built] == list(columns)

    @pytest.mark.django_db
    def test_a_scalar_column_stays_sortable_and_a_many_valued_one_does_not(self):
        # The changelist is read at database scale. A callable carries no sort key
        # unless one is set, so losing every sort key would be a regression the
        # specification never asked for.
        assert ColumnDisplay.build("qc").admin_order_field == "qc"
        # F12: quality_child now reads its own annotation key rather than a
        # shared "quality" accessor, so it sorts on its own key too.
        assert ColumnDisplay.build("quality_child").admin_order_field == "quality_child"
        # F12: Ref_IGSN is in the SCALAR group like any other scalar column,
        # so it stays sortable — first because sorting on a column that was
        # always "" was harmless, and now (FS-004) because it is a real value.
        assert ColumnDisplay.build("Ref_IGSN").admin_order_field == "Ref_IGSN"

        for unsortable in ("q_method", "corr_IS_flag"):
            assert not hasattr(ColumnDisplay.build(unsortable), "admin_order_field")

    def test_water_temperature_reads_the_renamed_surface_temperature_field(self):
        # The submission template and the published release are separate contracts
        # (specs/004-import-upload-template/decisions.md): US-7 renamed the model field
        # to ``surface_temperature`` because the value is not marine-only.

        class Row:
            surface_temperature = 3.0

        assert ColumnDisplay.build("water_temperature")(Row()) == 3.0


class TestBuiltCallablesAvoidTheFieldNameTrap:
    # Django resolves a ``list_display`` entry against the model's fields before the
    # admin's attributes, and reads ``short_description`` only when no field matches.

    @pytest.mark.django_db
    def test_a_column_named_after_a_model_field_still_renders_its_published_heading(
        self,
    ):
        # ``expedition`` and ``c_comment`` are fields on the determination model
        # whose ``verbose_name`` differs from the published column name.
        from django.contrib import admin

        from project.ghfdb.models import GHFDBChild

        model_admin = admin.site._registry[GHFDBChild]

        for name in ("expedition", "c_comment"):
            display = ColumnDisplay.build(name)
            bound = f"published_{name}"
            setattr(model_admin.__class__, bound, display)
            try:
                assert label_for_field(bound, GHFDBChild, model_admin) == name
            finally:
                delattr(model_admin.__class__, bound)

    @pytest.mark.django_db
    def test_binding_under_the_field_name_would_lose_the_heading(self):
        # The same two, bound the obvious way, prove the trap is real rather than
        # theoretical — otherwise the rule above reads as superstition.
        from django.contrib import admin

        from project.ghfdb.models import GHFDBChild

        model_admin = admin.site._registry[GHFDBChild]

        for name in ("expedition", "c_comment"):
            rendered = label_for_field(name, GHFDBChild, model_admin)
            assert rendered != name, (
                f"{name!r} was expected to render its field verbose_name"
            )
