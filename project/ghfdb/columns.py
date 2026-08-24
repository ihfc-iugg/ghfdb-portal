"""Published-column mapping for the GHFDB flat admin views.

R1 (``specs/002-ghfdb-proxy/research.md``) found that a published column's
value is reached one of four ways, and one trap: Django resolves a
``list_display`` string entry against the model's fields *before* the
admin's attributes, and reads a callable's ``short_description`` only when
no field matches. A callable bound under a name that is also a field name is
therefore silently ignored, and the field's own ``verbose_name`` is shown
instead — measured on the current changelists for ``expedition``,
``c_comment``, ``water_temperature`` and the leading identifier (D2).

``PublishedColumns`` holds one entry per published column — its group and
its accessor — and is the only place a published column name appears in
this module. ``ColumnDisplay`` turns an entry into a display callable, and
``ColumnDisplay.list_display_for()`` turns a canonical column list
(``constants.CHILD_COLUMNS`` or ``constants.PARENT_COLUMNS``) into those
callables, in that list's order, refusing — at call time, which for a
caller building ``list_display`` at class-body scope is import time — a
column this mapping does not hold.

References:
    - Fuchs et al. (2021). A new database structure for the IHFC Global Heat
      Flow Database. Earth System Science Data.
    - Fuchs et al. (2023). The Global Heat Flow Database: Update 2023.
"""

from collections.abc import Callable, Iterable
from typing import NamedTuple

from .constants import CORRECTION_COL_MAP


class ColumnEntry(NamedTuple):
    """A published column's group and how its value is reached.

    ``accessor`` defaults to the published name itself where the two
    coincide; it is set explicitly only where the value is read from a
    different attribute (``quality_child`` and ``quality_parent`` both read
    the single field ``quality`` — D2) or reached by a dotted path to a
    many-valued relationship.
    """

    group: str
    accessor: str | None = None


class PublishedColumns:
    """One entry per published column name: its group and its accessor.

    Four groups, per R1:

    * ``ANNOTATION`` — the value is a queryset annotation, already keyed
      under the published name by ``project/ghfdb/managers.py``.
    * ``FIELD`` — the value is a field on the proxy model itself, read
      directly rather than through an annotation.
    * ``MANY_VALUED`` — the value is a related manager, reached by a
      dot-separated attribute path from the row, and rendered as its
      members' labels joined with "; ".
    * ``EMPTY`` — nothing resolves the column (R4, D3); it renders as "".
    """

    ANNOTATION = "annotation"
    FIELD = "field"
    MANY_VALUED = "many_valued"
    EMPTY = "empty"

    ENTRIES: dict[str, ColumnEntry] = {
        # --- child: queryset annotations ------------------------------------
        # GHFDBChildQuerySet.as_ghfdb_flat() annotates each of these under
        # its own published name.
        "qc": ColumnEntry(ANNOTATION),
        "qc_uncertainty": ColumnEntry(ANNOTATION),
        "q_top": ColumnEntry(ANNOTATION),
        "q_bottom": ColumnEntry(ANNOTATION),
        "probe_penetration": ColumnEntry(ANNOTATION),
        "relevant_child": ColumnEntry(ANNOTATION),
        "corr_IS_flag": ColumnEntry(ANNOTATION),
        "corr_T_flag": ColumnEntry(ANNOTATION),
        "corr_S_flag": ColumnEntry(ANNOTATION),
        "corr_E_flag": ColumnEntry(ANNOTATION),
        "corr_TOPO_flag": ColumnEntry(ANNOTATION),
        "corr_PAL_flag": ColumnEntry(ANNOTATION),
        "corr_SUR_flag": ColumnEntry(ANNOTATION),
        "corr_CONV_flag": ColumnEntry(ANNOTATION),
        "corr_HR_flag": ColumnEntry(ANNOTATION),
        "probe_length": ColumnEntry(ANNOTATION),
        "probe_tilt": ColumnEntry(ANNOTATION),
        "T_grad_mean": ColumnEntry(ANNOTATION),
        "T_grad_uncertainty": ColumnEntry(ANNOTATION),
        "T_grad_mean_cor": ColumnEntry(ANNOTATION),
        "T_grad_uncertainty_cor": ColumnEntry(ANNOTATION),
        "T_shutin_top": ColumnEntry(ANNOTATION),
        "T_shutin_bottom": ColumnEntry(ANNOTATION),
        "T_number": ColumnEntry(ANNOTATION),
        "q_date": ColumnEntry(ANNOTATION),
        "tc_mean": ColumnEntry(ANNOTATION),
        "tc_uncertainty": ColumnEntry(ANNOTATION),
        "tc_number": ColumnEntry(ANNOTATION),
        # --- child: fields on the proxy itself ------------------------------
        "c_comment": ColumnEntry(FIELD),
        "expedition": ColumnEntry(FIELD),
        "water_temperature": ColumnEntry(FIELD),
        "quality_child": ColumnEntry(FIELD, "quality"),
        # --- child: many-valued relationships -------------------------------
        "q_method": ColumnEntry(MANY_VALUED, "method"),
        "probe_type": ColumnEntry(
            MANY_VALUED, "sample.heatflowinterval.probe_metadata.probe_type"
        ),
        "geo_lithology": ColumnEntry(MANY_VALUED, "sample.heatflowinterval.lithology"),
        "geo_stratigraphy": ColumnEntry(
            MANY_VALUED, "sample.heatflowinterval.stratigraphy"
        ),
        "T_method_top": ColumnEntry(MANY_VALUED, "thermal_gradient.method_top"),
        "T_method_bottom": ColumnEntry(MANY_VALUED, "thermal_gradient.method_bottom"),
        "T_corr_top": ColumnEntry(MANY_VALUED, "thermal_gradient.correction_top"),
        "T_corr_bottom": ColumnEntry(MANY_VALUED, "thermal_gradient.correction_bottom"),
        "tc_source": ColumnEntry(MANY_VALUED, "thermal_conductivity.source"),
        "tc_location": ColumnEntry(MANY_VALUED, "thermal_conductivity.location"),
        "tc_method": ColumnEntry(MANY_VALUED, "thermal_conductivity.method"),
        "tc_saturation": ColumnEntry(MANY_VALUED, "thermal_conductivity.saturation"),
        "tc_pT_conditions": ColumnEntry(
            MANY_VALUED, "thermal_conductivity.pT_conditions"
        ),
        "tc_pT_function": ColumnEntry(MANY_VALUED, "thermal_conductivity.pT_function"),
        "tc_strategy": ColumnEntry(MANY_VALUED, "thermal_conductivity.strategy"),
        # --- child: columns nothing resolves (R4, D3) -----------------------
        "publication_reference": ColumnEntry(EMPTY),
        "data_reference": ColumnEntry(EMPTY),
        "Ref_IGSN": ColumnEntry(EMPTY),
        # --- parent: queryset annotations ---------------------------------------
        # GHFDBParentQuerySet.as_ghfdb_flat() annotates each of these; the
        # published ``name`` is annotated as ``site_name`` because the
        # framework's base class already declares ``name`` (T048).
        "ID_parent": ColumnEntry(ANNOTATION),
        "q": ColumnEntry(ANNOTATION),
        "q_uncertainty": ColumnEntry(ANNOTATION),
        "name": ColumnEntry(ANNOTATION, "site_name"),
        "lat_NS": ColumnEntry(ANNOTATION),
        "long_EW": ColumnEntry(ANNOTATION),
        "elevation": ColumnEntry(ANNOTATION),
        "environment": ColumnEntry(ANNOTATION),
        "p_comment": ColumnEntry(ANNOTATION),
        "total_depth_MD": ColumnEntry(ANNOTATION),
        "total_depth_TVD": ColumnEntry(ANNOTATION),
        "explo_method": ColumnEntry(ANNOTATION),
        # --- parent: fields on the proxy itself -----------------------------------
        "corr_HP_flag": ColumnEntry(FIELD),
        "quality_parent": ColumnEntry(FIELD, "quality"),
        # --- parent: many-valued relationships ------------------------------------
        "explo_purpose": ColumnEntry(MANY_VALUED, "sample.heatflowsite.explo_purpose"),
    }


class ColumnDisplay:
    """Builds a display callable for one published column, per R1's four
    groups, and the ordered tuple a changelist's ``list_display`` takes.

    A callable's ``short_description`` is always the published name
    verbatim (D2). Every callable returned here is a fresh closure named
    ``display`` — never named after the published column it renders — so
    nothing built here can fall into the trap this module exists to avoid.
    """

    #: Correction flags are correlated subqueries, which the database cannot
    #: order by, so their callables carry no sort key. Every other scalar
    #: column can be sorted on.
    UNSORTABLE = frozenset(CORRECTION_COL_MAP)

    @staticmethod
    def annotation(accessor: str) -> Callable:
        """A callable reading *accessor* straight off an annotated row."""

        def display(obj):
            return getattr(obj, accessor, None)

        return display

    @staticmethod
    def field(accessor: str) -> Callable:
        """A callable reading *accessor* straight off the proxy model."""

        def display(obj):
            return getattr(obj, accessor, None)

        return display

    @staticmethod
    def many_valued(path: str) -> Callable:
        """A callable joining the labels of the related rows reached by
        *path*, a dot-separated attribute path from the row.

        A missing relationship anywhere along the path renders empty rather
        than raising.
        """
        segments = path.split(".")

        def display(obj):
            target = obj
            for segment in segments:
                target = getattr(target, segment, None)
                if target is None:
                    return ""
            return "; ".join(str(item) for item in target.all())

        return display

    @staticmethod
    def empty(accessor: str | None = None) -> Callable:
        """A callable for a column nothing resolves (R4, D3): always ''.

        Takes and ignores an accessor so :meth:`build` can call every
        group's builder the same way.
        """

        def display(obj):
            return ""

        return display

    @staticmethod
    def build(name: str) -> Callable:
        """Return the display callable for the published column *name*.

        Raises ``ValueError`` naming *name* if ``PublishedColumns`` holds no
        entry for it — the refusal SC-007 requires.
        """
        entry = PublishedColumns.ENTRIES.get(name)
        if entry is None:
            raise ValueError(f"{name!r} is not a published column this mapping covers.")

        builders = {
            PublishedColumns.ANNOTATION: ColumnDisplay.annotation,
            PublishedColumns.FIELD: ColumnDisplay.field,
            PublishedColumns.MANY_VALUED: ColumnDisplay.many_valued,
            PublishedColumns.EMPTY: ColumnDisplay.empty,
        }
        accessor = entry.accessor or name
        display = builders[entry.group](accessor)
        display.short_description = name

        # A scalar column stays sortable. The changelist is read at database
        # scale, so losing every sort key would be a regression, and a
        # many-valued or empty column has nothing to sort on.
        sortable = entry.group in (PublishedColumns.ANNOTATION, PublishedColumns.FIELD)
        if sortable and name not in ColumnDisplay.UNSORTABLE:
            display.admin_order_field = accessor
        return display

    @staticmethod
    def list_display_for(columns: Iterable[str]) -> tuple[Callable, ...]:
        """Return *columns* as display callables, in that order.

        Refuses — at call time, which for a caller building ``list_display``
        at class-body scope is import time — a column ``PublishedColumns``
        does not hold, naming it in the message (SC-007).
        """
        return tuple(ColumnDisplay.build(name) for name in columns)
