"""
Tests for GHFDBChildQuerySet and GHFDBChildManager.

Covers query-count guards, scalar column completeness, correction-flag annotations,
for_export() performance, and standard queryset operability.

Tests are written first (TDD); they will FAIL until the implementation is in place.
"""

import pytest


@pytest.mark.django_db
def test_as_ghfdb_flat_max_queries(django_assert_max_num_queries, heat_flow_chain):
    """
    T008: as_ghfdb_flat() must execute ≤2 DB queries, constant regardless of row count.
    """
    from project.ghfdb.models import GHFDB

    with django_assert_max_num_queries(2):
        results = list(GHFDB.objects.as_ghfdb_flat())

    assert len(results) >= 1


@pytest.mark.django_db
def test_as_ghfdb_flat_scalar_columns(heat_flow_chain):
    """
    T009: All 31 scalar annotations must be accessible as attributes on queryset records.
    """
    from project.ghfdb.models import GHFDB

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

    record = GHFDB.objects.as_ghfdb_flat().get(pk=heat_flow_chain.pk)

    for attr in expected_scalar_attrs:
        assert hasattr(record, attr), f"Missing scalar annotation: {attr}"


@pytest.mark.django_db
def test_as_ghfdb_flat_correction_flags(heat_flow_chain):
    """
    T010: All 9 corr_*_flag annotations must be accessible as attributes on queryset records.
    """
    from project.ghfdb.models import GHFDB

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

    record = GHFDB.objects.as_ghfdb_flat().get(pk=heat_flow_chain.pk)

    for attr in correction_flag_attrs:
        assert hasattr(record, attr), f"Missing correction flag annotation: {attr}"


@pytest.mark.django_db
def test_for_export_max_queries(django_assert_max_num_queries, heat_flow_chain):
    """
    T011: for_export() must execute ≤16 DB queries, constant regardless of row count.
    """
    from project.ghfdb.models import GHFDB

    with django_assert_max_num_queries(16):
        results = list(GHFDB.objects.for_export())

    assert len(results) >= 1


@pytest.mark.django_db
def test_as_ghfdb_flat_queryset_operations(heat_flow_chain):
    """
    T012: Standard queryset operations (filter, order_by, count) must work without error.
    """
    from project.ghfdb.models import GHFDB

    qs = GHFDB.objects.as_ghfdb_flat()

    count = qs.count()
    assert count >= 1

    filtered = qs.filter(pk=heat_flow_chain.pk)
    assert filtered.count() == 1

    ordered = list(qs.order_by("pk"))
    assert len(ordered) >= 1


# ---------------------------------------------------------------------------
# Phase 3b: GHFDBParent proxy queryset tests (T066–T069)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_parent_with_child_counts_max_queries(
    django_assert_max_num_queries, heat_flow_chain
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
def test_parent_with_child_counts_correctness(heat_flow_chain):
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
    django_assert_max_num_queries, heat_flow_chain
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
def test_parent_queryset_standard_operations(heat_flow_chain):
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


@pytest.mark.django_db
def test_ghfdb_child_manager_excludes_null_ghfdb_id(heat_flow_chain):
    """T094: GHFDB.objects (default manager) excludes records with ghfdb_id=None (FR-001b)."""
    from heat_flow.models import HeatFlow

    from project.ghfdb.models import GHFDB

    # Create a non-GHFDB HeatFlow record (ghfdb_id left as None)
    non_ghfdb = HeatFlow.objects.create(
        dataset=heat_flow_chain.dataset,
        sample=heat_flow_chain.sample,
        name="Non-GHFDB Child",
        value=50.0,
        parent=heat_flow_chain.parent,
    )
    assert non_ghfdb.ghfdb_id is None

    ghfdb_pks = set(GHFDB.objects.values_list("pk", flat=True))
    assert heat_flow_chain.pk in ghfdb_pks, (
        "Published GHFDB child must appear in default queryset"
    )
    assert non_ghfdb.pk not in ghfdb_pks, (
        "Non-GHFDB child (ghfdb_id=None) must be excluded"
    )


@pytest.mark.django_db
def test_ghfdb_parent_manager_excludes_null_ghfdb_id(heat_flow_chain):
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
