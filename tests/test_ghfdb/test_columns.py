"""Tests for the published-column mapping (``project/ghfdb/columns.py``).

T063 to T070. The mapping is the only place a published column name appears in
the admin, so these assert against ``constants.py`` rather than against a copy
of it — four copies of one list is what this feature exists to remove.
"""

import pytest
from django.contrib.admin.utils import label_for_field

from project.ghfdb.columns import ColumnDisplay, PublishedColumns
from project.ghfdb.constants import CHILD_COLUMNS, PARENT_COLUMNS

pytestmark = pytest.mark.ghfdb


class TestPublishedColumns:
    """The mapping from a published column name to how its value is reached,
    and the builder that turns a canonical column list into display callables
    (R1)."""

    def test_every_published_column_has_an_entry(self):
        """T063: every name in the canonical definitions is covered."""
        missing = [
            name
            for name in CHILD_COLUMNS + PARENT_COLUMNS
            if name not in PublishedColumns.ENTRIES
        ]
        assert missing == []

    def test_a_column_the_map_does_not_cover_is_refused_and_named(self):
        """T064 (SC-007): the gate is proven against the defect it exists to
        catch, not only against the passing case.

        A column added to the canonical definitions and not to the mapping is
        a startup failure rather than a silently missing column.
        """
        with pytest.raises(ValueError) as excinfo:
            ColumnDisplay.list_display_for([*CHILD_COLUMNS, "q_unmapped"])

        assert "q_unmapped" in str(excinfo.value)

    def test_each_heading_is_the_published_name_verbatim(self):
        """T065 (D2): including the four names the audit corrected."""
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
        """T066: R1 group one."""

        class Row:
            qc = 42.0

        assert ColumnDisplay.build("qc")(Row()) == 42.0

    def test_a_field_column_reads_the_field_and_can_override_its_heading(self):
        """T067: R1 group two, which is what lets one ``quality`` field appear
        as ``quality_child`` on one changelist and ``quality_parent`` on the
        other."""

        class Row:
            quality = "AAAA"

        for published in ("quality_child", "quality_parent"):
            display = ColumnDisplay.build(published)
            assert display(Row()) == "AAAA"
            assert display.short_description == published

    @pytest.mark.django_db
    def test_a_many_valued_column_joins_its_labels_and_issues_no_query_when_prefetched(
        self, django_assert_num_queries, sites_by_contribution
    ):
        """T068: R1 group three, and the N+1 this feature exists to avoid.

        Asserted against a literal read straight off the fixture's own
        many-to-many manager, not against the same "; ".join(...) expression
        re-derived through the callable under test — the previous version of
        this test compared ``ColumnDisplay.many_valued`` to itself and could
        not fail no matter what it returned. ``sites_by_contribution``'s
        ``all_contributing`` site carries two exploration purposes, so the
        expected value is genuinely populated rather than the empty string
        both sides would produce if the callable's body were replaced with
        ``return ""``.

        The zero-query assertion covers materialising the prefetched
        relationship itself, which is the N+1 ``with_children()`` exists to
        avoid. It does not wrap ``Concept.__str__`` — that reads a further
        FK (``vocabulary``) the M2M prefetch does not select-related, a cost
        that belongs to ``research_vocabs`` rather than to this mapping.
        """
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
        """T068: a missing relationship anywhere along the path renders empty
        rather than raising, which is FR-006 applied to the changelist."""

        class Row:
            thermal_gradient = None

        assert ColumnDisplay.build("T_method_top")(Row()) == ""

    def test_a_column_nothing_resolves_renders_empty(self):
        """T069: R1 group four and R4. Three columns are present and empty by
        decision, not by omission."""

        class Row:
            pass

        for name in ("Ref_IGSN", "publication_reference", "data_reference"):
            assert ColumnDisplay.build(name)(Row()) == ""

    def test_headings_are_the_canonical_order(self):
        """T070: the headings the built tuple produces equal the order
        ``constants.py`` gives.

        Headings rather than entry names: T077 records that Django resolves a
        ``list_display`` entry against the model's fields before the admin's
        attributes, so the two can disagree.
        """
        for columns in (CHILD_COLUMNS, PARENT_COLUMNS):
            built = ColumnDisplay.list_display_for(columns)
            assert [display.short_description for display in built] == list(columns)

    @pytest.mark.django_db
    def test_a_scalar_column_stays_sortable_and_a_many_valued_one_does_not(self):
        """The changelist is read at database scale. A callable carries no sort
        key unless one is set, so losing every sort key would be a regression
        the specification never asked for.
        """
        assert ColumnDisplay.build("qc").admin_order_field == "qc"
        assert ColumnDisplay.build("quality_child").admin_order_field == "quality"

        for unsortable in ("q_method", "Ref_IGSN", "corr_IS_flag"):
            assert not hasattr(ColumnDisplay.build(unsortable), "admin_order_field")


class TestBuiltCallablesAvoidTheFieldNameTrap:
    """Django resolves a ``list_display`` entry against the model's fields
    before the admin's attributes, and reads ``short_description`` only when no
    field matches. Four headings on the changelists were wrong for exactly that
    reason, so nothing built here may be bound under a field's name.
    """

    @pytest.mark.django_db
    def test_a_column_named_after_a_model_field_still_renders_its_published_heading(
        self,
    ):
        """T077. ``expedition``, ``c_comment`` and ``water_temperature`` are
        all fields on the determination model whose ``verbose_name`` differs
        from the published column name.
        """
        from django.contrib import admin

        from project.ghfdb.models import GHFDBChild

        model_admin = admin.site._registry[GHFDBChild]

        for name in ("expedition", "c_comment", "water_temperature"):
            display = ColumnDisplay.build(name)
            bound = f"published_{name}"
            setattr(model_admin.__class__, bound, display)
            try:
                assert label_for_field(bound, GHFDBChild, model_admin) == name
            finally:
                delattr(model_admin.__class__, bound)

    @pytest.mark.django_db
    def test_binding_under_the_field_name_would_lose_the_heading(self):
        """The same three, bound the obvious way, prove the trap is real rather
        than theoretical — otherwise the rule above reads as superstition."""
        from django.contrib import admin

        from project.ghfdb.models import GHFDBChild

        model_admin = admin.site._registry[GHFDBChild]

        for name in ("expedition", "c_comment", "water_temperature"):
            rendered = label_for_field(name, GHFDBChild, model_admin)
            assert rendered != name, (
                f"{name!r} was expected to render its field verbose_name"
            )
