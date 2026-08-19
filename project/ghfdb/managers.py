"""
GHFDB proxy queryset and manager.

Provides ``GHFDBChildQuerySet`` with two key methods:

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

from django.db.models import CharField, Count, F, OuterRef, Q, Subquery
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


class GHFDBChildQuerySet(PolymorphicQuerySet):
    """QuerySet for the ``GHFDBChild`` proxy model with flat-row annotation helpers."""

    def as_ghfdb_flat(self) -> "GHFDBChildQuerySet":
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

        Similarly, to reach the ``HeatFlowSite`` the path continues through
        the ``HeatFlowInterval.site`` FK::

            F("sample__heatflowinterval__site__elevation")
        """
        qs = self.select_related(
            "sample",
            "sample__heatflowinterval",
            "sample__heatflowinterval__site",
            "sample__heatflowinterval__site__location",
            "sample__heatflowinterval__probe_metadata",
            "parent",
            "thermal_gradient",
            "thermal_conductivity",
        )

        scalar_annotations = {
            # Child-level identifiers / values
            "ID_parent": F("parent__ghfdb_id"),
            "qc": F("value"),
            "qc_uncertainty": F("uncertainty"),
            "relevant_child": F("is_relevant"),
            "q_date": F("date_acquired"),
            # Site-level scalars (from HeatFlowSite via interval → site)
            # NOTE: 'name' conflicts with a Measurement base-class field; use
            # 'site_name' as the annotation key and export it via column_name.
            "site_name": F("sample__heatflowinterval__site__name"),
            "lat_NS": F("sample__heatflowinterval__site__location__y"),
            "long_EW": F("sample__heatflowinterval__site__location__x"),
            "elevation": F("sample__heatflowinterval__site__elevation"),
            "environment": F("sample__heatflowinterval__site__environment"),
            "explo_method": F("sample__heatflowinterval__site__explo_method"),
            "site_country": F("sample__heatflowinterval__site__country"),
            "site_region": F("sample__heatflowinterval__site__region"),
            "site_continent": F("sample__heatflowinterval__site__continent"),
            "site_domain": F("sample__heatflowinterval__site__domain"),
            "total_depth_MD": F("sample__heatflowinterval__site__length"),
            "total_depth_TVD": F("sample__heatflowinterval__site__vertical_depth"),
            # Parent heat flow scalars
            "q": F("parent__value"),
            "q_uncertainty": F("parent__uncertainty"),
            "corr_HP_flag": F("parent__corr_HP_flag"),
            "p_comment": F("parent__comment"),
            # Depth interval scalars (via HeatFlowInterval MTI accessor)
            "q_top": F("sample__heatflowinterval__top"),
            "q_bottom": F("sample__heatflowinterval__bottom"),
            # Thermal gradient scalars (GHFDB column names)
            "T_grad_mean": F("thermal_gradient__value"),
            "T_grad_uncertainty": F("thermal_gradient__uncertainty"),
            "T_grad_mean_cor": F("thermal_gradient__corrected_value"),
            "T_grad_uncertainty_cor": F("thermal_gradient__corrected_uncertainty"),
            "T_shutin_top": F("thermal_gradient__shutin_top"),
            "T_shutin_bottom": F("thermal_gradient__shutin_bottom"),
            "T_number": F("thermal_gradient__number"),
            # Thermal conductivity scalars
            "tc_mean": F("thermal_conductivity__value"),
            "tc_uncertainty": F("thermal_conductivity__uncertainty"),
            "tc_number": F("thermal_conductivity__number"),
            # Probe metadata scalars (via HeatFlowInterval MTI accessor)
            "probe_penetration": F(
                "sample__heatflowinterval__probe_metadata__penetration"
            ),
            "probe_length": F("sample__heatflowinterval__probe_metadata__length"),
            "probe_tilt": F("sample__heatflowinterval__probe_metadata__tilt"),
        }

        qs = qs.annotate(**scalar_annotations)
        qs = qs.annotate(**_correction_subqueries())
        return cast("GHFDBChildQuerySet", qs)

    def for_export(self) -> "GHFDBChildQuerySet":
        """
        Return a queryset ready for XLSX export: flat scalar annotations plus
        all 14 M2M relations pre-fetched.

        Executes ~16 DB queries total (1 main + 14 prefetch-related queries,
        one per M2M relation, plus optional content-type lookup), all constant
        regardless of row count.
        """
        qs = self.as_ghfdb_flat().prefetch_related(
            "method",
            "sample__heatflowinterval__site__explo_purpose",
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
        return cast("GHFDBChildQuerySet", qs)


class GHFDBChildManager(PolymorphicManager):
    """Custom manager for the ``GHFDBChild`` proxy model.

    Default queryset is scoped to records where ``ghfdb_id`` is set
    (FR-001b) — i.e. only published GHFDB entries are visible.
    """

    def get_queryset(self) -> GHFDBChildQuerySet:
        # cast: PolymorphicQuerySet is untyped, so .filter() erases to Any.
        return cast(
            GHFDBChildQuerySet,
            GHFDBChildQuerySet(self.model, using=self._db).filter(
                ghfdb_id__isnull=False
            ),
        )

    def as_ghfdb_flat(self) -> GHFDBChildQuerySet:
        """Delegate to ``GHFDBChildQuerySet.as_ghfdb_flat()``."""
        return self.get_queryset().as_ghfdb_flat()

    def for_export(self) -> GHFDBChildQuerySet:
        """Delegate to ``GHFDBChildQuerySet.for_export()``."""
        return self.get_queryset().for_export()


class GHFDBParentQuerySet(PolymorphicQuerySet):
    """QuerySet for the GHFDBParent proxy model with parent-level annotation helpers.

    References:
        - Fuchs et al. (2021). A new database structure for the IHFC Global Heat
          Flow Database. Earth System Science Data.
        - Fuchs et al. (2023). The Global Heat Flow Database: Update 2023.
    """

    def with_child_counts(self) -> "GHFDBParentQuerySet":
        """Annotate each parent record with child counts.

        Adds:
        - ``total_children`` — count of all linked ``HeatFlow`` children.
        - ``relevant_children`` — count of children where ``is_relevant=True``.

        Executes in a constant 1 DB query regardless of row count.
        """
        return cast(
            "GHFDBParentQuerySet",
            self.annotate(
                total_children=Count("children"),
                relevant_children=Count(
                    "children", filter=Q(children__is_relevant=True)
                ),
            ),
        )

    def with_children(self) -> "GHFDBParentQuerySet":
        """Prefetch linked child ``HeatFlow`` records.

        After calling this, accessing ``parent.children.all()`` will not fire
        additional queries.  Executes in ~2 DB queries (1 main + 1 prefetch),
        constant regardless of row count.
        """
        return cast("GHFDBParentQuerySet", self.prefetch_related("children"))

    def as_ghfdb_flat(self) -> "GHFDBParentQuerySet":
        """Annotate parent queryset with all scalar PARENT_COLUMNS fields.

        Annotation keys use canonical PARENT_COLUMNS names (e.g. ``'q'``,
        ``'lat_NS'``, ``'total_depth_MD'``).  The M2M field
        ``explo_purpose`` is excluded; callers must prefetch it separately.

        Executes ≤2 DB queries (main + optional content-type lookup),
        constant regardless of row count.
        """
        qs = self.select_related(
            "sample",
            "sample__location",
            "sample__heatflowsite",
        )
        scalar_annotations = {
            "ID_parent": F("ghfdb_id"),
            "q": F("value"),
            "q_uncertainty": F("uncertainty"),
            "p_comment": F("comment"),
            # NOTE: corr_HP_flag is a direct model field on HeatFlowParent;
            # it is accessible as obj.corr_HP_flag without annotation.
            # NOTE: 'name' conflicts with a Measurement base-class field; use
            # 'site_name' as the annotation key.
            "site_name": F("sample__name"),
            "lat_NS": F("sample__location__y"),
            "long_EW": F("sample__location__x"),
            "elevation": F("sample__heatflowsite__elevation"),
            "environment": F("sample__heatflowsite__environment"),
            "explo_method": F("sample__heatflowsite__explo_method"),
            "explo_purpose": F("sample__heatflowsite__explo_purpose"),
            "total_depth_MD": F("sample__heatflowsite__length"),
            "total_depth_TVD": F("sample__heatflowsite__vertical_depth"),
            "quality_parent": F("quality"),
        }
        return cast("GHFDBParentQuerySet", qs.annotate(**scalar_annotations))


class GHFDBParentManager(PolymorphicManager):
    """Custom manager for the ``GHFDBParent`` proxy model.

    Default queryset is scoped to records where ``ghfdb_id`` is set
    (FR-001b) — i.e. only published GHFDB parent entries are visible.
    """

    def get_queryset(self) -> GHFDBParentQuerySet:
        # cast: PolymorphicQuerySet is untyped, so .filter() erases to Any.
        return cast(
            GHFDBParentQuerySet,
            GHFDBParentQuerySet(self.model, using=self._db).filter(
                ghfdb_id__isnull=False
            ),
        )

    def with_child_counts(self) -> GHFDBParentQuerySet:
        """Delegate to ``GHFDBParentQuerySet.with_child_counts()``."""
        return self.get_queryset().with_child_counts()

    def with_children(self) -> GHFDBParentQuerySet:
        """Delegate to ``GHFDBParentQuerySet.with_children()``."""
        return self.get_queryset().with_children()

    def as_ghfdb_flat(self) -> GHFDBParentQuerySet:
        """Delegate to ``GHFDBParentQuerySet.as_ghfdb_flat()``."""
        return self.get_queryset().as_ghfdb_flat()
