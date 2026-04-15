"""
Tests for GHFDBQuerySet and GHFDBManager.

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
        "lat_ns",
        "long_ew",
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
        "interval_top",
        "interval_bottom",
        "tgrad_value",
        "tgrad_uncertainty",
        "tgrad_corrected",
        "tgrad_corrected_unc",
        "tgrad_shutin_top",
        "tgrad_shutin_bottom",
        "tgrad_number",
        "tc_value",
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
