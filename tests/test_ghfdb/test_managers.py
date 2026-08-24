"""Tests for the two proxy querysets and their managers.

Covers the membership scoping, the flattened published columns on each side,
the many-valued columns the flattening cannot carry, the query cost measured at
two row counts rather than one, and the page documenting all of it.
"""

import pathlib

import pytest

from project.ghfdb.columns import PublishedColumns
from project.ghfdb.constants import CHILD_COLUMNS, CORRECTION_COL_MAP

pytestmark = pytest.mark.ghfdb


def many_valued_reader(accessor):
    """Return a callable reading the related queryset at the dot-separated
    *accessor* off a row — the same path ``ColumnDisplay.many_valued``
    walks, stopped one step short of joining the labels, so a test can
    evaluate the queryset itself to prove no further query is issued.
    """
    segments = accessor.split(".")

    def read(row):
        target = row
        for segment in segments:
            target = getattr(target, segment)
        return target.all()

    return read


class TestGHFDBChildQuerySet:
    """GHFDBChildQuerySet.as_ghfdb_flat() and for_export() behaviour."""

    @pytest.mark.django_db
    def test_as_ghfdb_flat_queryset_operations(self, heat_flow_chain):
        """
        T012: Standard queryset operations (filter, order_by, count) must work without error.
        """
        from project.ghfdb.models import GHFDBChild

        qs = GHFDBChild.objects.as_ghfdb_flat()

        count = qs.count()
        assert count >= 1

        filtered = qs.filter(pk=heat_flow_chain.pk)
        assert filtered.count() == 1

        ordered = list(qs.order_by("pk"))
        assert len(ordered) >= 1


class TestChildExportQuerySet:
    """``for_export()``'s complete row (T024, T025, T027, T041).

    R3: seventeen published child columns are many-valued and cannot be
    annotated, so the complete row is read after ``for_export()`` rather
    than after ``as_ghfdb_flat()`` alone.
    """

    # The accessor for every CHILD_COLUMNS entry the published-column mapping
    # (``project/ghfdb/columns.py``) classifies as many-valued, read from
    # that mapping rather than restated here — the mapping is the one place
    # a published column's accessor is decided (D1).
    MANY_VALUED_CHILD_ACCESSORS = {
        name: many_valued_reader(entry.accessor)
        for name, entry in PublishedColumns.ENTRIES.items()
        if entry.group == PublishedColumns.MANY_VALUED and name in CHILD_COLUMNS
    }

    NOTHING_RESOLVES_CHILD_COLUMNS = frozenset(
        {"Ref_IGSN", "publication_reference", "data_reference"}
    )

    @pytest.mark.django_db
    def test_every_published_child_column_resolves_on_the_complete_row(
        self, published_chain
    ):
        """T024 (SC-001): every CHILD_COLUMNS entry — scalar, many-valued
        and the three that resolve to nothing — is readable on the row
        after ``for_export()``."""
        from project.ghfdb.constants import CHILD_COLUMNS
        from project.ghfdb.models import GHFDBChild

        record = GHFDBChild.objects.for_export().get(pk=published_chain.pk)

        for column in CHILD_COLUMNS:
            accessor = self.MANY_VALUED_CHILD_ACCESSORS.get(column)
            if accessor is not None:
                accessor(record)
            else:
                getattr(record, column)

    @pytest.mark.django_db
    def test_query_count_is_equal_at_two_row_counts(
        self, constant_query_count, published_chains
    ):
        """T025 (FR-007, SC-003)."""
        from project.ghfdb.models import GHFDBChild

        def call():
            list(GHFDBChild.objects.for_export())

        constant_query_count(published_chains, call)

    @pytest.mark.django_db
    def test_many_valued_columns_read_without_further_queries(
        self, django_assert_num_queries, published_chains
    ):
        """T026 (FR-007): after the queryset is evaluated, reading every
        many-valued column on every row costs nothing further."""
        from project.ghfdb.models import GHFDBChild

        published_chains(2)
        rows = list(GHFDBChild.objects.for_export())
        assert len(rows) == 2

        with django_assert_num_queries(0):
            for row in rows:
                for accessor in self.MANY_VALUED_CHILD_ACCESSORS.values():
                    list(accessor(row))

    @pytest.mark.django_db
    def test_columns_nothing_resolves_are_present_and_empty(self, published_chain):
        """T027 (FR-006): Ref_IGSN, publication_reference and
        data_reference are on the row and empty, per R4 and D3."""
        from project.ghfdb.models import GHFDBChild

        record = GHFDBChild.objects.for_export().get(pk=published_chain.pk)

        for column in self.NOTHING_RESOLVES_CHILD_COLUMNS:
            assert getattr(record, column) == ""


class TestGHFDBChildManager:
    """``GHFDBChildManager``'s default scoping (T013–T015)."""

    @pytest.mark.django_db
    def test_determination_without_a_published_identifier_is_absent(
        self, unpublished_chain
    ):
        """T013 (FR-002, SC-005): the unpublished chain's determination is
        absent from ``GHFDBChild.objects``, and present on ``HeatFlow.objects``
        so the fixture is proven to exist."""
        from heat_flow.models import HeatFlow

        from project.ghfdb.models import GHFDBChild

        assert HeatFlow.objects.filter(pk=unpublished_chain.pk).exists()
        assert not GHFDBChild.objects.filter(pk=unpublished_chain.pk).exists()

    @pytest.mark.django_db
    def test_scope_survives_filtering_ordering_counting_slicing_and_chaining(
        self, published_chain, unpublished_chain
    ):
        """T014 (FR-002, FR-003, SC-005): the published-only restriction
        holds after each operation, and after two chained together. R6
        records that the manager alone proves less than it appears to."""
        from project.ghfdb.models import GHFDBChild

        unpublished_pk = unpublished_chain.pk

        assert unpublished_pk not in set(
            GHFDBChild.objects.filter(pk__gt=0).values_list("pk", flat=True)
        )
        assert unpublished_pk not in set(
            GHFDBChild.objects.order_by("pk").values_list("pk", flat=True)
        )
        assert GHFDBChild.objects.count() == 1
        assert unpublished_pk not in {
            record.pk for record in GHFDBChild.objects.all()[:10]
        }
        assert unpublished_pk not in set(
            GHFDBChild.objects.filter(pk__gt=0)
            .order_by("pk")
            .values_list("pk", flat=True)
        )

    @pytest.mark.django_db
    def test_ordinary_operations_match_the_model_it_stands_in_for(
        self, published_chain, unpublished_chain
    ):
        """T015 (FR-003): filtering, ordering, counting and slicing through
        the proxy return what the same operations return on ``HeatFlow``
        restricted to published rows."""
        from heat_flow.models import HeatFlow

        from project.ghfdb.models import GHFDBChild

        reference = HeatFlow.objects.filter(ghfdb_id__isnull=False)

        assert GHFDBChild.objects.count() == reference.count()
        assert set(GHFDBChild.objects.values_list("pk", flat=True)) == set(
            reference.values_list("pk", flat=True)
        )
        assert list(GHFDBChild.objects.order_by("pk").values_list("pk", flat=True)) == list(
            reference.order_by("pk").values_list("pk", flat=True)
        )
        assert list(
            GHFDBChild.objects.order_by("pk")[:1].values_list("pk", flat=True)
        ) == list(reference.order_by("pk")[:1].values_list("pk", flat=True))


class TestChildFlattening:
    """``as_ghfdb_flat()``'s scalar annotation set (T016–T023, T032)."""

    # Published CHILD_COLUMNS reached only through a many-to-many relation
    # (verified against the model graph). Not read from constants.py: that
    # module holds the flat column list, not this classification of it.
    MANY_VALUED_CHILD_COLUMNS = frozenset(
        {
            "q_method",
            "probe_type",
            "geo_lithology",
            "geo_stratigraphy",
            "T_method_top",
            "T_method_bottom",
            "T_corr_top",
            "T_corr_bottom",
            "tc_source",
            "tc_location",
            "tc_method",
            "tc_saturation",
            "tc_pT_conditions",
            "tc_pT_function",
            "tc_strategy",
        }
    )

    # Published CHILD_COLUMNS with no data behind them at all (R4, D3).
    NOTHING_RESOLVES_CHILD_COLUMNS = frozenset(
        {"Ref_IGSN", "publication_reference", "data_reference"}
    )

    @pytest.mark.django_db
    def test_every_scalar_published_child_column_resolves_on_every_row(
        self, published_chains
    ):
        """T016 (FR-004): every CHILD_COLUMNS entry that is neither
        many-valued nor one of the three that resolve to nothing is
        readable, without error, on every row."""
        from project.ghfdb.constants import CHILD_COLUMNS
        from project.ghfdb.models import GHFDBChild

        scalar_columns = [
            column
            for column in CHILD_COLUMNS
            if column not in self.MANY_VALUED_CHILD_COLUMNS
            and column not in self.NOTHING_RESOLVES_CHILD_COLUMNS
        ]
        published_chains(2)

        for record in GHFDBChild.objects.as_ghfdb_flat():
            for column in scalar_columns:
                getattr(record, column)

    @pytest.mark.django_db
    def test_the_sites_representative_value_is_restated_on_every_row(
        self, published_chain
    ):
        """T017 (FR-004): the parent/site block reaches the child row,
        because the published file restates it per row."""
        from project.ghfdb.models import GHFDBChild

        site = published_chain.sample.site
        parent = published_chain.parent
        record = GHFDBChild.objects.as_ghfdb_flat().get(pk=published_chain.pk)

        assert record.site_name == site.name
        assert record.site_country == site.country
        assert record.site_continent == site.continent
        # The annotation reads the raw stored value; the descriptor on the
        # model instance resolves it to a Concept, so compare their string
        # forms rather than the objects themselves.
        assert str(record.environment) == str(site.environment)
        assert record.ID_parent == parent.ghfdb_id
        # QuantityField wraps the annotated value in a Quantity; compare
        # magnitudes rather than the object forms.
        assert getattr(record.q, "magnitude", record.q) == parent.value

    @pytest.mark.django_db
    def test_query_count_is_equal_at_two_row_counts(
        self, constant_query_count, published_chains
    ):
        """T018 (FR-005, SC-003), through the T010 helper."""
        from project.ghfdb.models import GHFDBChild

        def call():
            list(GHFDBChild.objects.as_ghfdb_flat())

        constant_query_count(published_chains, call)

    @pytest.mark.django_db
    def test_a_row_without_a_gradient_is_returned_with_those_columns_empty(
        self, chain_without_gradient
    ):
        """T019 (FR-006, SC-006): a missing gradient empties its own
        columns without dropping the row or raising."""
        from project.ghfdb.models import GHFDBChild

        record = GHFDBChild.objects.as_ghfdb_flat().get(pk=chain_without_gradient.pk)

        assert record.T_grad_mean is None
        assert record.T_grad_uncertainty is None
        assert record.T_grad_mean_cor is None
        assert record.T_grad_uncertainty_cor is None
        assert record.T_shutin_top is None
        assert record.T_shutin_bottom is None
        assert record.T_number is None

    @pytest.mark.django_db
    def test_a_row_without_a_conductivity_is_returned_with_those_columns_empty(
        self, chain_without_conductivity
    ):
        """T020 (FR-006, SC-006)."""
        from project.ghfdb.models import GHFDBChild

        record = GHFDBChild.objects.as_ghfdb_flat().get(
            pk=chain_without_conductivity.pk
        )

        assert record.tc_mean is None
        assert record.tc_uncertainty is None
        assert record.tc_number is None

    @pytest.mark.django_db
    def test_a_row_without_probe_metadata_is_returned_with_those_columns_empty(
        self, chain_without_probe_metadata
    ):
        """T021 (FR-006, SC-006)."""
        from project.ghfdb.models import GHFDBChild

        record = GHFDBChild.objects.as_ghfdb_flat().get(
            pk=chain_without_probe_metadata.pk
        )

        assert record.probe_penetration is None
        assert record.probe_length is None
        assert record.probe_tilt is None

    @pytest.mark.django_db
    @pytest.mark.parametrize("column_name", list(CORRECTION_COL_MAP))
    def test_a_missing_correction_leaves_only_its_own_column_empty(
        self, chain_missing_correction, column_name
    ):
        """T022 (FR-006, SC-006), parametrised over the nine correction
        types: SC-006 requires each one proven independently."""
        from project.ghfdb.models import GHFDBChild

        correction_type = CORRECTION_COL_MAP[column_name]
        child = chain_missing_correction(correction_type)
        record = GHFDBChild.objects.as_ghfdb_flat().get(pk=child.pk)

        assert getattr(record, column_name) is None
        for other_column, other_type in CORRECTION_COL_MAP.items():
            if other_type == correction_type:
                continue
            assert getattr(record, other_column) is not None

    @pytest.mark.django_db
    def test_annotations_carry_their_published_names(self):
        """T023 (FR-011): every annotation key equals its published column
        name, except a declared collision list, and each name on that list
        is checked to be a field the framework's base class actually
        declares. Without the second half the list is an escape hatch
        rather than a rule."""
        from heat_flow.models import HeatFlow

        from project.ghfdb.constants import CHILD_COLUMNS, PARENT_COLUMNS
        from project.ghfdb.models import GHFDBChild

        published_names = set(CHILD_COLUMNS) | set(PARENT_COLUMNS)
        annotation_keys = set(
            GHFDBChild.objects.as_ghfdb_flat().query.annotations.keys()
        )

        # FR-011: an annotation is prefixed only when the published name
        # collides with a field the base class (Measurement, via HeatFlow)
        # already declares.
        collision_list = {"site_name": "name"}
        for annotation_key, published_name in collision_list.items():
            assert annotation_key in annotation_keys
            assert published_name not in annotation_keys, (
                f"{published_name!r} is meant to collide and be renamed to "
                f"{annotation_key!r}, but both keys are present"
            )
            assert hasattr(HeatFlow, published_name), (
                f"{annotation_key!r} is on the collision list for "
                f"{published_name!r}, but HeatFlow does not declare that "
                "field"
            )

        # Annotations with no published-column counterpart at all: the
        # site geography columns D8 keeps outside the published shape,
        # added here only to support admin filtering.
        internal_only_annotations = {
            "site_country",
            "site_region",
            "site_continent",
            "site_domain",
        }

        unaccounted = (
            annotation_keys
            - published_names
            - set(collision_list)
            - internal_only_annotations
        )
        assert not unaccounted, f"unexplained annotation keys: {sorted(unaccounted)}"


class TestGHFDBParentManager:
    """``GHFDBParentManager``'s default scoping (T045).

    T044 is closed already: ``TestGHFDBManagerScoping::
    test_ghfdb_parent_manager_excludes_null_ghfdb_id`` below proves an
    unpublished site is absent from ``GHFDBParent.objects`` and present on
    ``ParentHeatFlow.objects``.
    """

    @pytest.mark.django_db
    def test_scope_survives_filtering_ordering_counting_slicing_and_chaining(
        self, published_chain, unpublished_chain
    ):
        """T045 (FR-002, FR-003, SC-005): the published-only restriction
        holds after each operation, and after two chained together."""
        from project.ghfdb.models import GHFDBParent

        unpublished_pk = unpublished_chain.parent.pk

        assert unpublished_pk not in set(
            GHFDBParent.objects.filter(pk__gt=0).values_list("pk", flat=True)
        )
        assert unpublished_pk not in set(
            GHFDBParent.objects.order_by("pk").values_list("pk", flat=True)
        )
        assert GHFDBParent.objects.count() == 1
        assert unpublished_pk not in {
            record.pk for record in GHFDBParent.objects.all()[:10]
        }
        assert unpublished_pk not in set(
            GHFDBParent.objects.filter(pk__gt=0)
            .order_by("pk")
            .values_list("pk", flat=True)
        )


class TestParentFlattening:
    """``GHFDBParentQuerySet.as_ghfdb_flat()``'s scalar annotation set
    (T046-T049, T059)."""

    # The one published PARENT_COLUMNS entry reached only through a
    # many-to-many relation. T059 excludes it from the annotations because
    # annotating a many-valued column with F() returns one row per value;
    # T062 prefetches it alongside the determinations instead.
    MANY_VALUED_PARENT_COLUMNS = frozenset({"explo_purpose"})

    # FR-011: the published ``name`` column collides with a field the
    # framework's base class declares, so it is annotated under a distinct
    # key. Every other PARENT_COLUMNS entry keeps its published name.
    COLLIDING_PARENT_COLUMNS = {"name": "site_name"}

    @pytest.mark.django_db
    def test_every_scalar_published_parent_column_resolves_on_every_row(
        self, sites_by_contribution
    ):
        """T046 (FR-008), T059: every PARENT_COLUMNS entry other than the
        one many-valued column is readable, without error, on every row —
        and the row count matches the number of sites rather than exploding
        on the site carrying two exploration purposes."""
        from project.ghfdb.constants import PARENT_COLUMNS
        from project.ghfdb.models import GHFDBParent

        scalar_columns = [
            column
            for column in PARENT_COLUMNS
            if column not in self.MANY_VALUED_PARENT_COLUMNS
        ]

        records = list(GHFDBParent.objects.as_ghfdb_flat())
        assert len(records) == len(sites_by_contribution)

        for record in records:
            for column in scalar_columns:
                accessor = self.COLLIDING_PARENT_COLUMNS.get(column, column)
                getattr(record, accessor)

    @pytest.mark.django_db
    def test_query_count_is_equal_at_two_row_counts(
        self, constant_query_count, published_chains
    ):
        """T047 (FR-008, SC-003)."""
        from project.ghfdb.models import GHFDBParent

        def call():
            list(GHFDBParent.objects.as_ghfdb_flat())

        constant_query_count(published_chains, call)

    @pytest.mark.django_db
    def test_the_colliding_site_name_is_annotated_distinctly(self, published_chain):
        """T048 (FR-011): the published ``name`` column is annotated under a
        distinct name because the framework's base class declares ``name``,
        and the published name is restored at the surface that presents
        it."""
        from heat_flow.models import ParentHeatFlow

        from project.ghfdb.models import GHFDBParent

        parent = published_chain.parent
        record = GHFDBParent.objects.as_ghfdb_flat().get(pk=parent.pk)

        assert hasattr(ParentHeatFlow, "name")
        assert record.site_name == parent.sample.name

    @pytest.mark.django_db
    def test_a_column_that_does_not_collide_keeps_its_published_name(
        self, published_chain
    ):
        """T049 (FR-011): elevation is annotated as ``elevation``, not under
        a prefix. D6 settles this, and the rule is only readable if a
        non-colliding case is pinned alongside a colliding one."""
        from project.ghfdb.models import GHFDBParent

        site = published_chain.parent.sample
        site.elevation = 123.0
        site.save(update_fields=["elevation"])

        record = GHFDBParent.objects.as_ghfdb_flat().get(
            pk=published_chain.parent.pk
        )

        assert getattr(record.elevation, "magnitude", record.elevation) == 123.0


class TestParentCounts:
    """``with_child_counts()``'s determination counts (T050-T052)."""

    @pytest.mark.django_db
    def test_counts_are_correct_for_all_some_and_no_contributing_determinations(
        self, sites_by_contribution
    ):
        """T050 (FR-009, SC-004): the counts are correct across the four
        contribution shapes SC-004 names."""
        from project.ghfdb.models import GHFDBParent

        records = {
            record.pk: record for record in GHFDBParent.objects.with_child_counts()
        }

        all_contributing = sites_by_contribution["all_contributing"]
        some_contributing = sites_by_contribution["some_contributing"]
        none_contributing = sites_by_contribution["none_contributing"]

        assert records[all_contributing.pk].total_children == 2
        assert records[all_contributing.pk].relevant_children == 2

        assert records[some_contributing.pk].total_children == 2
        assert records[some_contributing.pk].relevant_children == 1

        assert records[none_contributing.pk].total_children == 2
        assert records[none_contributing.pk].relevant_children == 0

    @pytest.mark.django_db
    def test_a_site_with_no_determinations_counts_zero_rather_than_empty(
        self, sites_by_contribution
    ):
        """T051 (FR-009, SC-004): the distinction between a count of zero
        and a null is the assertion."""
        from project.ghfdb.models import GHFDBParent

        no_determinations = sites_by_contribution["no_determinations"]
        record = GHFDBParent.objects.with_child_counts().get(pk=no_determinations.pk)

        assert record.total_children == 0
        assert record.relevant_children == 0
        assert record.total_children is not None
        assert record.relevant_children is not None

    @pytest.mark.django_db
    def test_query_count_is_equal_at_two_row_counts(
        self, constant_query_count, published_chains
    ):
        """T052 (FR-009, SC-003)."""
        from project.ghfdb.models import GHFDBParent

        def call():
            list(GHFDBParent.objects.with_child_counts())

        constant_query_count(published_chains, call)


class TestParentChildAttachment:
    """``with_children()``'s determination attachment (T053, T054)."""

    @pytest.mark.django_db
    def test_reading_each_sites_determinations_costs_no_query_per_site(
        self, django_assert_num_queries, published_chains
    ):
        """T053 (FR-010): iterating every site's determinations after
        evaluation costs no query per site."""
        from project.ghfdb.models import GHFDBParent

        published_chains(2)
        records = list(GHFDBParent.objects.with_children())
        assert len(records) == 2

        with django_assert_num_queries(0):
            for record in records:
                list(record.children.all())

    @pytest.mark.django_db
    def test_query_count_is_equal_at_two_row_counts(
        self, constant_query_count, published_chains
    ):
        """T054 (FR-010, SC-003)."""
        from project.ghfdb.models import GHFDBParent

        def call():
            records = list(GHFDBParent.objects.with_children())
            for record in records:
                list(record.children.all())

        constant_query_count(published_chains, call)


class TestParentPublishedColumns:
    """The complete published parent row (T055)."""

    @pytest.mark.django_db
    def test_every_published_parent_column_resolves_on_the_complete_row(
        self, sites_by_contribution
    ):
        """T055 (SC-002): every PARENT_COLUMNS entry — scalar and the one
        many-valued column — is readable on the row after flattening and
        attachment together (R3), since the many-valued column cannot be
        annotated. Read on the site carrying two exploration purposes, so a
        reintroduced ``F()`` annotation that duplicates rows is caught.

        This does not assert a zero further-query cost for
        ``explo_purpose``: D11 records that the matching prefetch T062 also
        asks for is blocked by a pre-existing test in direct, provable
        conflict with it.
        """
        from project.ghfdb.constants import PARENT_COLUMNS
        from project.ghfdb.models import GHFDBParent

        collision = TestParentFlattening.COLLIDING_PARENT_COLUMNS
        all_contributing = sites_by_contribution["all_contributing"]

        record = (
            GHFDBParent.objects.as_ghfdb_flat()
            .with_children()
            .get(pk=all_contributing.pk)
        )

        for column in PARENT_COLUMNS:
            if column == "explo_purpose":
                purposes = list(record.sample.heatflowsite.explo_purpose.all())
                assert len(purposes) == 2
            else:
                getattr(record, collision.get(column, column))


# ---------------------------------------------------------------------------
# Phase 3b: GHFDBParent proxy queryset tests (T066–T069)
# ---------------------------------------------------------------------------


class TestGHFDBParentQuerySet:
    """GHFDBParent proxy queryset methods: with_child_counts(), with_children()."""

    @pytest.mark.django_db
    def test_parent_with_child_counts_correctness(self, heat_flow_chain):
        """
        T067 (US1b): total_children and relevant_children counts must be correct.

        The heat_flow_chain fixture creates exactly 1 HeatFlow child; is_relevant
        defaults to True on HeatFlow, so relevant_children should also be 1.
        """
        from project.ghfdb.models import GHFDBParent

        heat_flow_chain.is_relevant = True
        heat_flow_chain.save(update_fields=["is_relevant"])

        parent = GHFDBParent.objects.with_child_counts().get(pk=heat_flow_chain.parent.pk)
        assert parent.total_children == 1
        assert parent.relevant_children == 1

    @pytest.mark.django_db
    def test_parent_queryset_standard_operations(self, heat_flow_chain):
        """
        T069 (US1b): Standard queryset operations work on GHFDBParent.objects.all().
        """
        from project.ghfdb.models import GHFDBParent

        qs = GHFDBParent.objects.all()
        assert qs.count() >= 1
        assert qs.filter(pk=heat_flow_chain.parent.pk).count() == 1
        assert len(list(qs.order_by("pk"))) >= 1


# ---------------------------------------------------------------------------
# Phase 8: Queryset scoping tests (T094) — FR-001b
# ---------------------------------------------------------------------------


class TestGHFDBManagerScoping:
    """Default managers exclude records with ghfdb_id=None (FR-001b)."""

    @pytest.mark.django_db
    def test_ghfdb_child_manager_excludes_null_ghfdb_id(self, heat_flow_chain):
        """T094: GHFDBChild.objects (default manager) excludes records with ghfdb_id=None (FR-001b)."""
        from heat_flow.models import HeatFlow

        from project.ghfdb.models import GHFDBChild

        # Create a non-GHFDB HeatFlow record (ghfdb_id left as None)
        non_ghfdb = HeatFlow.objects.create(
            dataset=heat_flow_chain.dataset,
            sample=heat_flow_chain.sample,
            name="Non-GHFDB Child",
            value=50.0,
            parent=heat_flow_chain.parent,
        )
        assert non_ghfdb.ghfdb_id is None

        ghfdb_pks = set(GHFDBChild.objects.values_list("pk", flat=True))
        assert heat_flow_chain.pk in ghfdb_pks, (
            "Published GHFDB child must appear in default queryset"
        )
        assert non_ghfdb.pk not in ghfdb_pks, (
            "Non-GHFDB child (ghfdb_id=None) must be excluded"
        )

    @pytest.mark.django_db
    def test_ghfdb_parent_manager_excludes_null_ghfdb_id(self, heat_flow_chain):
        """T094: GHFDBParent.objects (default manager) excludes parents with ghfdb_id=None (FR-001b)."""
        # Create a distinct site (one parent-per-site constraint prevents reusing the chain site)
        from heat_flow.models import HeatFlowSite, ParentHeatFlow

        from project.ghfdb.models import GHFDBParent

        other_site = HeatFlowSite.objects.create(
            dataset=heat_flow_chain.dataset,
            name="Non-GHFDB Site",
            country="Germany",
            continent="Europe",
            environment="onshore_continental",
        )
        # Create a non-GHFDB parent (ghfdb_id left as None)
        non_ghfdb_parent = ParentHeatFlow.objects.create(
            dataset=heat_flow_chain.dataset,
            sample=other_site,
            name="Non-GHFDB Parent",
            value=55.0,
        )
        assert non_ghfdb_parent.ghfdb_id is None

        ghfdb_parent_pks = set(GHFDBParent.objects.values_list("pk", flat=True))
        assert heat_flow_chain.parent.pk in ghfdb_parent_pks, (
            "Published GHFDB parent must appear in default queryset"
        )
        assert non_ghfdb_parent.pk not in ghfdb_parent_pks, (
            "Non-GHFDB parent (ghfdb_id=None) must be excluded"
        )


PUBLISHED_STRUCTURE_PAGE = (
    pathlib.Path(__file__).parents[2] / "docs" / "data_models" / "published-structure.md"
)


class TestPublishedStructurePage:
    def test_the_page_exists_and_is_in_the_navigation(self):
        assert PUBLISHED_STRUCTURE_PAGE.exists()
        index = (PUBLISHED_STRUCTURE_PAGE.parent / "index.md").read_text()
        assert "published-structure" in index

    def test_it_names_every_public_queryset_method_this_feature_defines(self):
        """Read from the modules, so a method added or renamed without a
        documentation change fails here."""
        import inspect

        from project.ghfdb.managers import GHFDBChildQuerySet, GHFDBParentQuerySet

        page = PUBLISHED_STRUCTURE_PAGE.read_text()
        for queryset in (GHFDBChildQuerySet, GHFDBParentQuerySet):
            for name, member in inspect.getmembers(queryset, inspect.isfunction):
                if name.startswith("_") or member.__module__ != queryset.__module__:
                    continue
                assert f"{name}()" in page, f"{queryset.__name__}.{name}() undocumented"

    def test_it_names_the_two_corrected_column_spellings(self):
        """The page is where a curator finds out why the header they know is
        not the header they see."""
        page = PUBLISHED_STRUCTURE_PAGE.read_text()
        for corrected in ("tc_pT_function", "Ref_IGSN"):
            assert corrected in page

    def test_it_names_the_columns_that_are_always_empty(self):
        page = PUBLISHED_STRUCTURE_PAGE.read_text()
        for empty in ("Ref_IGSN", "publication_reference", "data_reference"):
            assert empty in page
