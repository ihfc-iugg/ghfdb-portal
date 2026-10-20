"""What a heat flow record's overview page lists beyond FairDM's shared page.

Every related record a page lists passes FairDM's own visibility rule, ``visible_to``, so a
record a visitor may not open is counted and never named.
"""

from fairdm.core.measurement.models import Measurement
from fairdm.core.sample.models import Sample

from heat_flow.models import (
    HeatFlow,
    HeatFlowInterval,
    HeatFlowSite,
    IntervalConductivity,
    ParentHeatFlow,
    ThermalGradient,
)
from heat_flow.quality import SCHEME_REVISION


class HeatFlowPage:
    """What a heat flow record's overview page lists, for one visitor.

    Attributes:
        intervals_shown: How many of a site's intervals its page lists before the cut.
        children_shown: How many children a list shows before the cut.
    """

    intervals_shown = 20
    children_shown = 20

    def __init__(self, record, user, show_all=False):
        """Hold the record a page is for and the visitor reading it.

        Args:
            record: The heat flow record whose overview page is being rendered.
            user: The visitor, signed in or anonymous.
            show_all: Lift the cut on a site's list of intervals.
        """
        self.record = record
        self.user = user
        self.show_all = show_all

    def context(self):
        """Gather what the record's page shows, by the record's type.

        Returns:
            The page's content, as the type's ``for_*`` method describes it.
        """
        gather = {
            HeatFlowSite: self.for_site,
            HeatFlowInterval: self.for_interval,
            HeatFlow: self.for_child,
            ThermalGradient: self.for_gradient_or_conductivity,
            IntervalConductivity: self.for_gradient_or_conductivity,
            ParentHeatFlow: self.for_parent,
        }[type(self.record)]
        return gather()

    def opens(self, record):
        """Say whether a record's own page would open for the visitor.

        Args:
            record: A sample or measurement, or ``None``.

        Returns:
            ``True`` when the record exists and FairDM lets the visitor open it.
        """
        return record is not None and bool(self.split([record])[0])

    def split(self, records):
        """Separate the records the visitor may open from those they may not.

        Makes one query however many records it is given. The records must all be
        samples or all be measurements.

        Args:
            records: The records to check, samples or measurements.

        Returns:
            The records the visitor may open, in the order given, and how many they may not.
        """
        records = list(records)
        if not records:
            return [], 0
        base = Sample if isinstance(records[0], Sample) else Measurement
        opened = set(
            base.objects.filter(pk__in=[record.pk for record in records])
            .visible_to(self.user)
            .values_list("pk", flat=True)
        )
        shown = [record for record in records if record.pk in opened]
        return shown, len(records) - len(shown)

    def listing(self, children, limit=None):
        """Cut a list of children to the ones the visitor may open.

        Args:
            children: The child heat flow values a page would list.
            limit: How many to show; every one the visitor may open when ``None``.

        Returns:
            The ``rows`` to show, the ``total`` the visitor may open, how many ``more`` the
            cut leaves out, and how many are ``hidden`` from the visitor.
        """
        visible, hidden = self.split(children)
        rows = visible[:limit] if limit else visible
        return {
            "rows": rows,
            "total": len(visible),
            "more": len(visible) - len(rows),
            "hidden": hidden,
        }

    def site_location(self):
        """Gather the location of the record's site, as the site's.

        Returns:
            The ``site``, whether the visitor may see it (``visible``), and its ``point``,
            ``elevation`` and ``uncertainty``. Nothing of the site when the visitor may not
            open it.
        """
        record = self.record
        if isinstance(record, (HeatFlowInterval, ParentHeatFlow)):
            site = record.site
        else:
            site = getattr(record.sample, "site", None)
        if site is None:
            return {"site": None, "visible": False, "point": None}
        visible = self.opens(site)
        return {
            "site": site if visible else None,
            "visible": visible,
            "point": site.location if visible else None,
            "elevation": site.location_elevation if visible else None,
            "uncertainty": site.location_uncertainty if visible else None,
        }

    @staticmethod
    def is_stale(record):
        """Say whether a stored score came from a scheme revision other than the current one.

        Args:
            record: A record carrying a ``quality_scheme``.

        Returns:
            ``True`` when the record was scored under another revision. A record not yet
            scored is not stale.
        """
        return bool(record.quality_scheme) and record.quality_scheme != SCHEME_REVISION

    def for_site(self):
        """Gather a site's parent value and its intervals with their children.

        Intervals run from shallowest to deepest, by top, then bottom, then primary key.
        Each shown interval carries its children. The cut at ``intervals_shown`` is lifted
        by ``show_all``.

        Returns:
            The ``parent`` the visitor may open, or ``None``, and ``parent_hidden`` when the
            site has a parent the visitor may not open. The ``intervals``: the ``rows`` to
            show, each an ``interval`` and its ``children`` (``rows`` and ``hidden``), the
            ``total`` the visitor may open, how many ``more`` the cut leaves out, how many
            are ``hidden`` from the visitor and the ``children`` counted over every
            interval the visitor may open.
        """
        site = self.record
        parent = ParentHeatFlow.objects.filter(sample=site).first()
        parent_opens = self.opens(parent)
        intervals = list(
            HeatFlowInterval.objects.filter(site=site)
            .prefetch_related("lithology")
            .order_by("top", "bottom", "pk")
        )
        visible, hidden = self.split(intervals)
        shown = visible if self.show_all else visible[: self.intervals_shown]
        children = list(
            HeatFlow.objects.filter(sample__in=shown)
            .prefetch_related("method")
            .order_by("pk")
        )
        opened, _ = self.split(children)
        opened_pks = {child.pk for child in opened}
        rows = []
        for interval in shown:
            over = [child for child in children if child.sample_id == interval.pk]
            listed = [child for child in over if child.pk in opened_pks]
            rows.append(
                {
                    "interval": interval,
                    "children": {"rows": listed, "hidden": len(over) - len(listed)},
                }
            )
        return {
            "parent": parent if parent_opens else None,
            "parent_hidden": parent is not None and not parent_opens,
            "intervals": {
                "rows": rows,
                "total": len(visible),
                "more": len(visible) - len(shown),
                "hidden": hidden,
                "children": HeatFlow.objects.filter(sample__in=visible).count(),
            },
        }

    def for_interval(self):
        """Gather an interval's site and probe metadata."""
        interval = self.record
        site = interval.site
        return {
            "site": site if self.opens(site) else None,
            "site_hidden": site is not None and not self.opens(site),
            "probe": getattr(interval, "probe_metadata", None),
            "location": self.site_location(),
        }

    def for_child(self):
        """Gather what a child heat flow value was calculated from and belongs to.

        Returns:
            The ``gradient``, ``conductivity`` and ``parent`` the visitor may open, each
            ``None`` when absent or hidden, with ``gradient_hidden``, ``conductivity_hidden``
            and ``parent_hidden`` set when it exists but the visitor may not open it. Also the
            child's ``corrections``, the ``interval`` and ``site`` it was made on, the site's
            ``location`` and whether its scores are ``stale``.
        """
        child = self.record
        related = {
            "gradient": child.thermal_gradient,
            "conductivity": child.thermal_conductivity,
            "parent": child.parent,
        }
        measurements = [record for record in related.values() if record is not None]
        opened, _ = self.split(measurements)
        interval = child.sample
        site = getattr(interval, "site", None)
        placed = [record for record in (interval, site) if record is not None]
        samples, _ = self.split(placed)
        context = {}
        for name, record in related.items():
            context[name] = record if record in opened else None
            context[f"{name}_hidden"] = record is not None and record not in opened
        return {
            **context,
            "corrections": list(child.corrections.all()),
            "interval": interval if interval in samples else None,
            "site": site if site in samples else None,
            "location": self.site_location(),
            "stale": self.is_stale(child),
        }

    def for_gradient_or_conductivity(self):
        """Gather the children that use a gradient or a conductivity."""
        measurement = self.record
        interval = measurement.sample
        site = getattr(interval, "site", None)
        return {
            "interval": interval if self.opens(interval) else None,
            "site": site if self.opens(site) else None,
            "location": self.site_location(),
            "children": self.listing(
                measurement.heat_flow_children.order_by("pk"), self.children_shown
            ),
            "stale": self.is_stale(measurement),
        }

    def for_parent(self):
        """Gather a parent's children and the ones its quality rests on."""
        parent = self.record
        children = list(parent.children.order_by("-is_relevant", "pk"))
        if len(children) == 1:
            rests_on = {children[0].pk}
            basis = "single"
        else:
            rests_on = {child.pk for child in children if child.is_relevant}
            basis = "relevant" if rests_on else ("none" if children else "empty")
        for child in children:
            child.rests_on = child.pk in rests_on
        return {
            "children": self.listing(children, self.children_shown),
            "rests_on": rests_on,
            "basis": basis,
            "site": parent.sample if self.opens(parent.sample) else None,
            "location": self.site_location(),
            "stale": self.is_stale(parent),
        }
