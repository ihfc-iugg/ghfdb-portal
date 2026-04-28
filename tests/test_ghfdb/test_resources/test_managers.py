"""
T092 — BUG-010: Queryset annotation key alignment tests.

Verifies that:
- GHFDBChildQuerySet.as_ghfdb_flat() uses canonical annotation key names
  (e.g. "q" not "p_q", "name" not "site_name", "corr_HP_flag" not "p_corr_hp_flag")
- GHFDBParentQuerySet exposes as_ghfdb_flat() and its keys match PARENT_COLUMNS names
- Stale prefixed/lowercase keys are absent after BUG-010 implementation

These tests FAIL until T096 (rename child annotation keys) and T097 (add parent
as_ghfdb_flat()) are implemented.
"""

import pytest


# ---------------------------------------------------------------------------
# T092 — GHFDBChildQuerySet.as_ghfdb_flat() canonical key tests
# ---------------------------------------------------------------------------


class TestGHFDBChildQuerySetAnnotationKeys:
    """GHFDBChildQuerySet.as_ghfdb_flat() must use canonical GHFDB column names."""

    @pytest.mark.django_db
    def test_canonical_parent_value_key(self):
        """Annotation key for parent heat flow value must be 'q', not 'p_q' (BUG-010)."""
        from project.ghfdb.models import GHFDB

        qs = GHFDB.objects.none().as_ghfdb_flat()
        annotations = qs.query.annotations
        assert "q" in annotations, "Canonical annotation 'q' missing (BUG-010 T096)"
        assert "p_q" not in annotations, "Stale annotation 'p_q' still present (BUG-010 T096)"

    @pytest.mark.django_db
    def test_canonical_parent_uncertainty_key(self):
        """Annotation key for parent uncertainty must be 'q_uncertainty', not 'p_q_uncertainty' (BUG-010)."""
        from project.ghfdb.models import GHFDB

        qs = GHFDB.objects.none().as_ghfdb_flat()
        annotations = qs.query.annotations
        assert "q_uncertainty" in annotations, "Canonical annotation 'q_uncertainty' missing (BUG-010)"
        assert "p_q_uncertainty" not in annotations, "Stale annotation 'p_q_uncertainty' still present (BUG-010)"

    @pytest.mark.django_db
    def test_site_name_annotation_present(self):
        """Annotation 'site_name' must exist for the site-name value (BUG-010).

        'name' cannot be used as annotation key because it conflicts with the
        Measurement base-class field; 'site_name' is the designated workaround.
        """
        from project.ghfdb.models import GHFDB

        qs = GHFDB.objects.none().as_ghfdb_flat()
        annotations = qs.query.annotations
        assert "site_name" in annotations, "Annotation 'site_name' missing — site name not accessible (BUG-010 T096)"

    @pytest.mark.django_db
    def test_canonical_elevation_key(self):
        """Annotation key for elevation must be 'elevation', not 'site_elevation' (BUG-010)."""
        from project.ghfdb.models import GHFDB

        qs = GHFDB.objects.none().as_ghfdb_flat()
        annotations = qs.query.annotations
        assert "elevation" in annotations, "Canonical annotation 'elevation' missing (BUG-010)"
        assert "site_elevation" not in annotations, "Stale annotation 'site_elevation' still present (BUG-010)"

    @pytest.mark.django_db
    def test_canonical_corr_hp_flag_key(self):
        """Annotation key for HP correction flag must be 'corr_HP_flag', not 'p_corr_hp_flag' (BUG-010)."""
        from project.ghfdb.models import GHFDB

        qs = GHFDB.objects.none().as_ghfdb_flat()
        annotations = qs.query.annotations
        assert "corr_HP_flag" in annotations, "Canonical annotation 'corr_HP_flag' missing (BUG-010)"
        assert "p_corr_hp_flag" not in annotations, "Stale annotation 'p_corr_hp_flag' still present (BUG-010)"

    @pytest.mark.django_db
    def test_canonical_total_depth_md_key(self):
        """Annotation key for total depth MD must be 'total_depth_MD', not 'total_depth_md' (BUG-010)."""
        from project.ghfdb.models import GHFDB

        qs = GHFDB.objects.none().as_ghfdb_flat()
        annotations = qs.query.annotations
        assert "total_depth_MD" in annotations, "Canonical annotation 'total_depth_MD' missing (BUG-010)"
        assert "total_depth_md" not in annotations, "Stale annotation 'total_depth_md' still present (BUG-010)"

    @pytest.mark.django_db
    def test_canonical_total_depth_tvd_key(self):
        """Annotation key for total depth TVD must be 'total_depth_TVD', not 'total_depth_tvd' (BUG-010)."""
        from project.ghfdb.models import GHFDB

        qs = GHFDB.objects.none().as_ghfdb_flat()
        annotations = qs.query.annotations
        assert "total_depth_TVD" in annotations, "Canonical annotation 'total_depth_TVD' missing (BUG-010)"
        assert "total_depth_tvd" not in annotations, "Stale annotation 'total_depth_tvd' still present (BUG-010)"

    @pytest.mark.django_db
    def test_canonical_id_parent_key(self):
        """Annotation key for ID_parent must be 'ID_parent', not 'id_parent' (BUG-010)."""
        from project.ghfdb.models import GHFDB

        qs = GHFDB.objects.none().as_ghfdb_flat()
        annotations = qs.query.annotations
        assert "ID_parent" in annotations, "Canonical annotation 'ID_parent' missing (BUG-010)"
        assert "id_parent" not in annotations, "Stale annotation 'id_parent' still present (BUG-010)"

    @pytest.mark.django_db
    def test_canonical_explo_method_key(self):
        """Annotation key for explo_method must be 'explo_method', not 'site_explo_method' (BUG-010)."""
        from project.ghfdb.models import GHFDB

        qs = GHFDB.objects.none().as_ghfdb_flat()
        annotations = qs.query.annotations
        assert "explo_method" in annotations, "Canonical annotation 'explo_method' missing (BUG-010)"
        assert "site_explo_method" not in annotations, "Stale annotation 'site_explo_method' still present (BUG-010)"

    @pytest.mark.django_db
    def test_lat_ns_and_long_ew_preserved(self):
        """lat_NS and long_EW annotation keys must be preserved (already canonical) (BUG-010)."""
        from project.ghfdb.models import GHFDB

        qs = GHFDB.objects.none().as_ghfdb_flat()
        annotations = qs.query.annotations
        assert "lat_NS" in annotations, "Annotation 'lat_NS' must be preserved"
        assert "long_EW" in annotations, "Annotation 'long_EW' must be preserved"


# ---------------------------------------------------------------------------
# T092 — GHFDBParentQuerySet.as_ghfdb_flat() existence test
# ---------------------------------------------------------------------------


class TestGHFDBParentQuerySetFlatMethod:
    """GHFDBParentQuerySet must expose as_ghfdb_flat() (BUG-010 T097)."""

    def test_parent_queryset_has_as_ghfdb_flat(self):
        """GHFDBParentQuerySet must have an as_ghfdb_flat() method (BUG-010).

        This test FAILS until T097 is implemented.
        """
        from project.ghfdb.managers import GHFDBParentQuerySet

        assert hasattr(GHFDBParentQuerySet, "as_ghfdb_flat"), (
            "GHFDBParentQuerySet missing as_ghfdb_flat() — implement T097 (BUG-010)"
        )
        assert callable(GHFDBParentQuerySet.as_ghfdb_flat)

    def test_parent_manager_has_as_ghfdb_flat(self):
        """GHFDBParentManager must expose as_ghfdb_flat() delegate (BUG-010)."""
        from project.ghfdb.managers import GHFDBParentManager

        assert hasattr(GHFDBParentManager, "as_ghfdb_flat"), (
            "GHFDBParentManager missing as_ghfdb_flat() delegate — implement T097 (BUG-010)"
        )

    @pytest.mark.django_db
    def test_parent_queryset_flat_returns_canonical_keys(self):
        """GHFDBParentQuerySet.as_ghfdb_flat() must annotate with canonical PARENT_COLUMNS keys (BUG-010)."""
        from project.ghfdb.managers import GHFDBParentQuerySet
        from project.ghfdb.models import GHFDBParent

        if not hasattr(GHFDBParentQuerySet, "as_ghfdb_flat"):
            pytest.skip("GHFDBParentQuerySet.as_ghfdb_flat() not yet implemented (T097)")

        qs = GHFDBParent.objects.none().as_ghfdb_flat()
        annotations = qs.query.annotations
        # 'name' cannot be used as annotation key (conflicts with Measurement base field);
        # the workaround annotation is 'site_name'.
        # 'corr_HP_flag' is a direct model field on HeatFlowParent; no annotation needed.
        for key in ("q", "q_uncertainty", "site_name", "lat_NS", "long_EW", "elevation"):
            assert key in annotations, (
                f"GHFDBParentQuerySet.as_ghfdb_flat() missing canonical annotation '{key}' (BUG-010)"
            )
