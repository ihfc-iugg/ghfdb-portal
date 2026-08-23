"""
Tests for GHFDBChildQuerySet and GHFDBChildManager.

Covers query-count guards, scalar column completeness, correction-flag annotations,
for_export() performance, and standard queryset operability.

Tests are written first (TDD); they will FAIL until the implementation is in place.
"""

import pytest

from project.ghfdb.constants import CORRECTION_COL_MAP

pytestmark = pytest.mark.ghfdb


class TestGHFDBChildQuerySet:
    """GHFDBChildQuerySet.as_ghfdb_flat() and for_export() behaviour."""

    @pytest.mark.django_db
    def test_as_ghfdb_flat_max_queries(self, django_assert_max_num_queries, heat_flow_chain):
        """
        T008: as_ghfdb_flat() must execute ≤2 DB queries, constant regardless of row count.
        """
        from project.ghfdb.models import GHFDBChild

        with django_assert_max_num_queries(2):
            results = list(GHFDBChild.objects.as_ghfdb_flat())

        assert len(results) >= 1

    @pytest.mark.xfail(strict=True, reason=(
        "Half-landed GHFDB canonical column work: the constants moved to the "
        "published spreadsheet casing, but ghfdb_colmeta.json, the resource "
        "field declarations and one manager annotation key did not follow. "
        "Needs debugging, and a decision on the published column vocabulary, "
        "before it can pass. See issue #122."
    ))
    @pytest.mark.django_db
    def test_as_ghfdb_flat_scalar_columns(self, heat_flow_chain):
        """
        T009: All 31 scalar annotations must be accessible as attributes on queryset records.
        """
        from project.ghfdb.models import GHFDBChild

        expected_scalar_attrs = [
            "site_name",
            "lat_NS",
            "long_EW",
            "site_elevation",
            "site_environment",
            "site_explo_method",
            "site_country",
            "site_region",
            "site_continent",
            "site_domain",
            "total_depth_md",
            "total_depth_tvd",
            "p_q",
            "p_q_uncertainty",
            "p_corr_hp_flag",
            "p_comment",
            "q_top",
            "q_bottom",
            "T_grad_mean",
            "T_grad_uncertainty",
            "T_grad_mean_cor",
            "T_grad_uncertainty_cor",
            "T_shutin_top",
            "T_shutin_bottom",
            "T_number",
            "tc_mean",
            "tc_uncertainty",
            "tc_number",
            "probe_penetration",
            "probe_length",
            "probe_tilt",
        ]

        record = GHFDBChild.objects.as_ghfdb_flat().get(pk=heat_flow_chain.pk)

        for attr in expected_scalar_attrs:
            assert hasattr(record, attr), f"Missing scalar annotation: {attr}"

    @pytest.mark.django_db
    def test_as_ghfdb_flat_correction_flags(self, heat_flow_chain):
        """
        T010: All 9 corr_*_flag annotations must be accessible as attributes on queryset records.
        """
        from project.ghfdb.models import GHFDBChild

        correction_flag_attrs = [
            "corr_IS_flag",
            "corr_T_flag",
            "corr_S_flag",
            "corr_E_flag",
            "corr_TOPO_flag",
            "corr_PAL_flag",
            "corr_SUR_flag",
            "corr_CONV_flag",
            "corr_HR_flag",
        ]

        record = GHFDBChild.objects.as_ghfdb_flat().get(pk=heat_flow_chain.pk)

        for attr in correction_flag_attrs:
            assert hasattr(record, attr), f"Missing correction flag annotation: {attr}"

    @pytest.mark.django_db
    def test_for_export_max_queries(self, django_assert_max_num_queries, heat_flow_chain):
        """
        T011: for_export() must execute ≤16 DB queries, constant regardless of row count.
        """
        from project.ghfdb.models import GHFDBChild

        with django_assert_max_num_queries(16):
            results = list(GHFDBChild.objects.for_export())

        assert len(results) >= 1

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


# ---------------------------------------------------------------------------
# Phase 3b: GHFDBParent proxy queryset tests (T066–T069)
# ---------------------------------------------------------------------------


class TestGHFDBParentQuerySet:
    """GHFDBParent proxy queryset methods: with_child_counts(), with_children()."""

    @pytest.mark.django_db
    def test_parent_with_child_counts_max_queries(
        self, django_assert_max_num_queries, heat_flow_chain
    ):
        """
        T066 (US1b): with_child_counts() must execute in a constant number of DB
        queries with no N+1 per parent row.
        """
        from project.ghfdb.models import GHFDBParent

        with django_assert_max_num_queries(3):
            results = list(GHFDBParent.objects.with_child_counts())

        assert len(results) >= 1

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
    def test_parent_with_children_no_extra_queries(
        self, django_assert_max_num_queries, heat_flow_chain
    ):
        """
        T068 (US1b): with_children() must attach child HeatFlow objects accessible
        without extra queries (prefetch_related).
        """
        from project.ghfdb.models import GHFDBParent

        with django_assert_max_num_queries(3):
            parents = list(GHFDBParent.objects.with_children())
            for p in parents:
                _ = list(p.children.all())  # must not fire extra queries due to prefetch

        assert len(parents) >= 1

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
