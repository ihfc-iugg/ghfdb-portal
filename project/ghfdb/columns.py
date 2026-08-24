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

from collections.abc import Iterable
from typing import Any, NamedTuple, Protocol, cast

from .constants import CORRECTION_COL_MAP


class DisplayCallable(Protocol):
    """What Django asks of a ``list_display`` entry that is a callable.

    ``short_description`` is the column heading, and every callable
    ``ColumnDisplay.build`` returns carries it. ``admin_order_field`` — the
    sort key — is deliberately not part of this protocol (F11): it is set
    only on a sortable scalar column's callable, so declaring it here as
    always present would claim an attribute the many-valued and empty
    builders never set, exactly what the ``hasattr`` check in
    ``test_a_scalar_column_stays_sortable_and_a_many_valued_one_does_not``
    depends on being false.
    """

    short_description: str

    def __call__(self, obj: Any) -> Any: ...


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

    Three groups, per R1:

    * ``SCALAR`` — a single value read straight off the row: either a
      queryset annotation, already keyed under the published name by
      ``project/ghfdb/managers.py``, or a field on the proxy model itself.
      Both are read identically here — ``getattr(obj, accessor, None)`` does
      not care which one put the value on the row — so this mapping does not
      carry the distinction as two groups (F10). Some published columns
      arrive one way, some the other; that is a fact about ``managers.py``,
      not about how this mapping reads them.
    * ``MANY_VALUED`` — the value is a related manager, reached by a
      dot-separated attribute path from the row, and rendered as its
      members' labels joined with "; ".
    * ``EMPTY`` — nothing resolves the column (R4, D3); it renders as "".
    """

    SCALAR = "scalar"
    MANY_VALUED = "many_valued"
    EMPTY = "empty"

    ENTRIES: dict[str, ColumnEntry] = {
        # --- child: scalar columns -------------------------------------------
        # Most of these are queryset annotations GHFDBChildQuerySet.as_ghfdb_flat()
        # keys under the published name; a few are fields on the proxy itself.
        "qc": ColumnEntry(SCALAR),
        "qc_uncertainty": ColumnEntry(SCALAR),
        "q_top": ColumnEntry(SCALAR),
        "q_bottom": ColumnEntry(SCALAR),
        "probe_penetration": ColumnEntry(SCALAR),
        "relevant_child": ColumnEntry(SCALAR),
        "corr_IS_flag": ColumnEntry(SCALAR),
        "corr_T_flag": ColumnEntry(SCALAR),
        "corr_S_flag": ColumnEntry(SCALAR),
        "corr_E_flag": ColumnEntry(SCALAR),
        "corr_TOPO_flag": ColumnEntry(SCALAR),
        "corr_PAL_flag": ColumnEntry(SCALAR),
        "corr_SUR_flag": ColumnEntry(SCALAR),
        "corr_CONV_flag": ColumnEntry(SCALAR),
        "corr_HR_flag": ColumnEntry(SCALAR),
        "probe_length": ColumnEntry(SCALAR),
        "probe_tilt": ColumnEntry(SCALAR),
        "T_grad_mean": ColumnEntry(SCALAR),
        "T_grad_uncertainty": ColumnEntry(SCALAR),
        "T_grad_mean_cor": ColumnEntry(SCALAR),
        "T_grad_uncertainty_cor": ColumnEntry(SCALAR),
        "T_shutin_top": ColumnEntry(SCALAR),
        "T_shutin_bottom": ColumnEntry(SCALAR),
        "T_number": ColumnEntry(SCALAR),
        "q_date": ColumnEntry(SCALAR),
        "tc_mean": ColumnEntry(SCALAR),
        "tc_uncertainty": ColumnEntry(SCALAR),
        "tc_number": ColumnEntry(SCALAR),
        # --- child: fields on the proxy itself (also SCALAR — see class docstring) ---
        "c_comment": ColumnEntry(SCALAR),
        "expedition": ColumnEntry(SCALAR),
        "water_temperature": ColumnEntry(SCALAR),
        "quality_child": ColumnEntry(SCALAR, "quality"),
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
        # --- parent: scalar columns ----------------------------------------------
        # Most of these are queryset annotations GHFDBParentQuerySet.as_ghfdb_flat()
        # keys under the published name; the published ``name`` is annotated as
        # ``site_name`` because the framework's base class already declares
        # ``name`` (T048).
        "ID_parent": ColumnEntry(SCALAR),
        "q": ColumnEntry(SCALAR),
        "q_uncertainty": ColumnEntry(SCALAR),
        "name": ColumnEntry(SCALAR, "site_name"),
        "lat_NS": ColumnEntry(SCALAR),
        "long_EW": ColumnEntry(SCALAR),
        "elevation": ColumnEntry(SCALAR),
        "environment": ColumnEntry(SCALAR),
        "p_comment": ColumnEntry(SCALAR),
        "total_depth_MD": ColumnEntry(SCALAR),
        "total_depth_TVD": ColumnEntry(SCALAR),
        "explo_method": ColumnEntry(SCALAR),
        # --- parent: fields on the proxy itself (also SCALAR — see class docstring) --
        "corr_HP_flag": ColumnEntry(SCALAR),
        "quality_parent": ColumnEntry(SCALAR, "quality"),
        # --- parent: many-valued relationships ------------------------------------
        "explo_purpose": ColumnEntry(MANY_VALUED, "sample.heatflowsite.explo_purpose"),
    }


class ColumnDisplay:
    """Builds a display callable for one published column, per
    ``PublishedColumns``'s three groups, and the ordered tuple a
    changelist's ``list_display`` takes.

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
    def scalar(accessor: str) -> DisplayCallable:
        """A callable reading *accessor* straight off the row — an
        annotation or a field, whichever ``managers.py`` happens to carry it
        as (F10, D14's ``PublishedColumns`` docstring)."""

        def display(obj):
            return getattr(obj, accessor, None)

        return cast(DisplayCallable, display)

    @staticmethod
    def many_valued(path: str) -> DisplayCallable:
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

        return cast(DisplayCallable, display)

    @staticmethod
    def empty(accessor: str | None = None) -> DisplayCallable:
        """A callable for a column nothing resolves (R4, D3): always ''.

        Takes and ignores an accessor so :meth:`build` can call every
        group's builder the same way.
        """

        def display(obj):
            return ""

        return cast(DisplayCallable, display)

    @staticmethod
    def build(name: str) -> DisplayCallable:
        """Return the display callable for the published column *name*.

        Raises ``ValueError`` naming *name* if ``PublishedColumns`` holds no
        entry for it — the refusal SC-007 requires.
        """
        entry = PublishedColumns.ENTRIES.get(name)
        if entry is None:
            raise ValueError(f"{name!r} is not a published column this mapping covers.")

        builders = {
            PublishedColumns.SCALAR: ColumnDisplay.scalar,
            PublishedColumns.MANY_VALUED: ColumnDisplay.many_valued,
            PublishedColumns.EMPTY: ColumnDisplay.empty,
        }
        accessor = entry.accessor or name
        # Typed loosely until the two attributes below are set, then cast to
        # the narrower ``DisplayCallable`` on return: ``admin_order_field``
        # is deliberately not part of that protocol (F11), since it is never
        # present on the many-valued or empty groups' callables, so
        # assigning it through the protocol type would be a claim the
        # protocol itself does not make.
        display: Any = builders[entry.group](accessor)
        display.short_description = name

        # A scalar column stays sortable. The changelist is read at database
        # scale, so losing every sort key would be a regression, and a
        # many-valued or empty column has nothing to sort on.
        sortable = entry.group == PublishedColumns.SCALAR
        if sortable and name not in ColumnDisplay.UNSORTABLE:
            display.admin_order_field = accessor
        return cast(DisplayCallable, display)

    @staticmethod
    def list_display_for(columns: Iterable[str]) -> tuple[DisplayCallable, ...]:
        """Return *columns* as display callables, in that order.

        Refuses — at call time, which for a caller building ``list_display``
        at class-body scope is import time — a column ``PublishedColumns``
        does not hold, naming it in the message (SC-007).
        """
        return tuple(ColumnDisplay.build(name) for name in columns)
