"""
GHFDB proxy queryset and manager.

Provides ``GHFDBQuerySet`` with two key methods:

* ``as_ghfdb_flat()`` — annotates all 31 scalar columns via ``select_related``
  and ``F()`` expressions, plus 9 correction-flag subqueries; ≤2 DB queries,
  constant regardless of row count.

* ``for_export()`` — calls ``as_ghfdb_flat()`` and chains
  ``prefetch_related()`` for all 14 M2M paths; ~16 DB queries, constant.

References:
    - Fuchs et al. (2021). A new database structure for the IHFC Global Heat
      Flow Database. Earth System Science Data.
    - Fuchs et al. (2023). The Global Heat Flow Database: Update 2023.
"""

from typing import Any, cast

from django.db.models import CharField, F, OuterRef, Subquery
from polymorphic.managers import PolymorphicManager, PolymorphicQuerySet


def _correction_subqueries() -> dict[str, Subquery]:
    """Return 9 correlated Subquery annotations, one per correction type.

    Each subquery selects ``HeatFlowCorrection.status`` for the given
    ``correction_type``, keyed as ``corr_{type}_flag``.  Because
    ``unique_together = [("heat_flow", "correction_type")]`` holds,
    each subquery is satisfied by an index-only scan.
    """
    from heat_flow.models import HeatFlowCorrection

    annotations: dict[str, Subquery] = {}
    correction_model = cast(Any, HeatFlowCorrection)
    for choice_value, _label in correction_model.CorrectionTypeChoices.choices:
        col_name = f"corr_{choice_value}_flag"
        annotations[col_name] = Subquery(
            correction_model.objects.filter(
                heat_flow=OuterRef("pk"),
                correction_type=choice_value,
            ).values("status")[:1],
            output_field=CharField(),
        )
    return annotations


class GHFDBQuerySet(PolymorphicQuerySet):
    """QuerySet for the GHFDB proxy model with flat-row annotation helpers."""

    def as_ghfdb_flat(self) -> "GHFDBQuerySet":
        """
        Annotate the queryset with all 31 scalar GHFDB columns and 9
        correction-flag subqueries.

        Executes ≤2 DB queries total (main query + optional content-type
        lookup), regardless of the number of rows returned.

        Scalar columns are sourced via ``select_related`` traversal and
        ``F()`` expressions; correction flags via correlated subqueries.

        Implementation note — MTI traversal
        ------------------------------------
        ``HeatFlow.sample`` (FK on ``Measurement``) points to the
        ``Sample`` polymorphic root, NOT directly to ``HeatFlowInterval``.
        To reach ``HeatFlowInterval``-specific fields (depth columns,
        probe metadata) the MTI child accessor ``heatflowinterval`` must be
        used in the lookup path, e.g.::

            F("sample__heatflowinterval__top")

        Similarly, to reach the parent ``HeatFlowSite`` the path traverses
        the ``HeatFlowInterval.sample`` FK *through* the MTI accessor::

            F("sample__heatflowinterval__sample__heatflowsite__elevation")
        """
        qs = self.select_related(
            "sample",
            "sample__heatflowinterval",
            "sample__heatflowinterval__sample",
            "sample__heatflowinterval__sample__location",
            "sample__heatflowinterval__sample__heatflowsite",
            "sample__heatflowinterval__probe_metadata",
            "parent",
            "thermal_gradient",
            "thermal_conductivity",
        )

        scalar_annotations = {
            # Site-level scalars (from HeatFlowSite via interval → site)
            "site_name": F("sample__heatflowinterval__sample__name"),
            "lat_ns": F("sample__heatflowinterval__sample__location__y"),
            "long_ew": F("sample__heatflowinterval__sample__location__x"),
            "site_elevation": F("sample__heatflowinterval__sample__heatflowsite__elevation"),
            "site_environment": F("sample__heatflowinterval__sample__heatflowsite__environment"),
            "site_explo_method": F("sample__heatflowinterval__sample__heatflowsite__explo_method"),
            "site_country": F("sample__heatflowinterval__sample__heatflowsite__country"),
            "site_region": F("sample__heatflowinterval__sample__heatflowsite__region"),
            "site_continent": F("sample__heatflowinterval__sample__heatflowsite__continent"),
            "site_domain": F("sample__heatflowinterval__sample__heatflowsite__domain"),
            "total_depth_md": F("sample__heatflowinterval__sample__heatflowsite__length"),
            "total_depth_tvd": F("sample__heatflowinterval__sample__heatflowsite__vertical_depth"),
            # Parent heat flow scalars
            "p_q": F("parent__value"),
            "p_q_uncertainty": F("parent__uncertainty"),
            "p_corr_hp_flag": F("parent__corr_HP_flag"),
            "p_comment": F("parent__comment"),
            # Depth interval scalars (via HeatFlowInterval MTI accessor)
            "interval_top": F("sample__heatflowinterval__top"),
            "interval_bottom": F("sample__heatflowinterval__bottom"),
            # Thermal gradient scalars
            "tgrad_value": F("thermal_gradient__value"),
            "tgrad_uncertainty": F("thermal_gradient__uncertainty"),
            "tgrad_corrected": F("thermal_gradient__corrected_value"),
            "tgrad_corrected_unc": F("thermal_gradient__corrected_uncertainty"),
            "tgrad_shutin_top": F("thermal_gradient__shutin_top"),
            "tgrad_shutin_bottom": F("thermal_gradient__shutin_bottom"),
            "tgrad_number": F("thermal_gradient__number"),
            # Thermal conductivity scalars
            "tc_value": F("thermal_conductivity__value"),
            "tc_uncertainty": F("thermal_conductivity__uncertainty"),
            "tc_number": F("thermal_conductivity__number"),
            # Probe metadata scalars (via HeatFlowInterval MTI accessor)
            "probe_penetration": F("sample__heatflowinterval__probe_metadata__penetration"),
            "probe_length": F("sample__heatflowinterval__probe_metadata__length"),
            "probe_tilt": F("sample__heatflowinterval__probe_metadata__tilt"),
        }

        qs = qs.annotate(**scalar_annotations)
        qs = qs.annotate(**_correction_subqueries())
        return cast("GHFDBQuerySet", qs)

    def for_export(self) -> "GHFDBQuerySet":
        """
        Return a queryset ready for XLSX export: flat scalar annotations plus
        all 14 M2M relations pre-fetched.

        Executes ~16 DB queries total (1 main + 14 prefetch-related queries,
        one per M2M relation, plus optional content-type lookup), all constant
        regardless of row count.
        """
        qs = self.as_ghfdb_flat().prefetch_related(
            "method",
            "sample__heatflowinterval__sample__heatflowsite__explo_purpose",
            "thermal_gradient__method_top",
            "thermal_gradient__method_bottom",
            "thermal_gradient__correction_top",
            "thermal_gradient__correction_bottom",
            "thermal_conductivity__source",
            "thermal_conductivity__location",
            "thermal_conductivity__method",
            "thermal_conductivity__saturation",
            "thermal_conductivity__pT_conditions",
            "thermal_conductivity__pT_function",
            "thermal_conductivity__strategy",
            "sample__heatflowinterval__probe_metadata__probe_type",
        )
        return cast("GHFDBQuerySet", qs)


class GHFDBManager(PolymorphicManager):
    """Custom manager for the GHFDB proxy model."""

    def get_queryset(self) -> GHFDBQuerySet:
        return GHFDBQuerySet(self.model, using=self._db)

    def as_ghfdb_flat(self) -> GHFDBQuerySet:
        """Delegate to ``GHFDBQuerySet.as_ghfdb_flat()``."""
        return self.get_queryset().as_ghfdb_flat()

    def for_export(self) -> GHFDBQuerySet:
        """Delegate to ``GHFDBQuerySet.for_export()``."""
        return self.get_queryset().for_export()
