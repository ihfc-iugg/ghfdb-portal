"""What the heat flow overview pages read beyond FairDM's shared sample and measurement pages.

SKETCH: this module gathers each heat flow page's context for the prototype. Where it lives and
how it reaches the page (plugin methods, a template tag) is for the plan to decide.

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

INTERVALS_SHOWN = 20
CHILDREN_SHOWN = 20


def visible_ids(model, ids, user):
    """Return the ids among ``ids`` whose own page would open for ``user``."""
    base = Sample if issubclass(model, Sample) else Measurement
    return set(
        base.objects.filter(pk__in=ids).visible_to(user).values_list("pk", flat=True)
    )


def is_visible(record, user):
    """Say whether ``record``'s own page would open for ``user``."""
    if record is None:
        return False
    return bool(visible_ids(type(record), [record.pk], user))


def is_stale(record):
    """Say whether a stored score came from a scheme revision other than the current one."""
    return bool(record.quality_scheme) and record.quality_scheme != SCHEME_REVISION


def site_of(record):
    """Return the heat flow site a record belongs to, or ``None``."""
    if isinstance(record, HeatFlowSite):
        return record
    if isinstance(record, HeatFlowInterval):
        return record.site
    sample = getattr(record, "sample", None)
    if sample is None:
        return None
    return site_of(sample)


def site_location(record, user):
    """Return the site's location as a page shows it, with whether the visitor may see it."""
    site = site_of(record)
    if site is None:
        return {"site": None, "visible": False, "point": None}
    visible = is_visible(site, user)
    return {
        "site": site if visible else None,
        "visible": visible,
        "point": site.location if visible else None,
        "elevation": site.location_elevation if visible else None,
        "uncertainty": site.location_uncertainty if visible else None,
    }


def child_rows(children, user, limit=CHILDREN_SHOWN):
    """Return the children the visitor may open, up to ``limit``, and the counts."""
    children = list(children)
    shown_ids = visible_ids(HeatFlow, [c.pk for c in children], user)
    visible = [c for c in children if c.pk in shown_ids]
    return {
        "rows": visible[:limit] if limit else visible,
        "total": len(visible),
        "more": max(len(visible) - limit, 0) if limit else 0,
        "hidden": len(children) - len(visible),
    }


def site_context(site, user, show_all=False):
    """Gather a site's parent value and its intervals with their children."""
    parent = ParentHeatFlow.objects.filter(sample=site).first()
    intervals = list(
        HeatFlowInterval.objects.filter(site=site).order_by("top", "bottom", "pk")
    )
    shown_ids = visible_ids(HeatFlowInterval, [i.pk for i in intervals], user)
    visible = [i for i in intervals if i.pk in shown_ids]
    shown = visible if show_all else visible[:INTERVALS_SHOWN]
    children = HeatFlow.objects.filter(sample__in=shown).order_by("pk")
    by_interval = {}
    for child in children:
        by_interval.setdefault(child.sample_id, []).append(child)
    rows = []
    for interval in shown:
        rows.append(
            {
                "interval": interval,
                "children": child_rows(by_interval.get(interval.pk, []), user, None),
            }
        )
    return {
        "parent": parent if is_visible(parent, user) else None,
        "parent_hidden": parent is not None and not is_visible(parent, user),
        "intervals": {
            "rows": rows,
            "total": len(visible),
            "more": len(visible) - len(shown),
            "hidden": len(intervals) - len(visible),
            "children": HeatFlow.objects.filter(sample__in=visible).count(),
        },
    }


def interval_context(interval, user):
    """Gather an interval's site and probe metadata."""
    site = interval.site
    return {
        "site": site if is_visible(site, user) else None,
        "site_hidden": site is not None and not is_visible(site, user),
        "probe": getattr(interval, "probe_metadata", None),
        "location": site_location(interval, user),
    }


def measured_on(measurement, user):
    """Gather the interval and site a measurement was made on."""
    interval = measurement.sample
    site = interval.site if isinstance(interval, HeatFlowInterval) else None
    return {
        "interval": interval if is_visible(interval, user) else None,
        "site": site if is_visible(site, user) else None,
        "location": site_location(measurement, user),
    }


def child_context(child, user):
    """Gather what a child heat flow value was calculated from and belongs to."""
    gradient, conductivity, parent = (
        child.thermal_gradient,
        child.thermal_conductivity,
        child.parent,
    )
    return {
        **measured_on(child, user),
        "gradient": gradient if is_visible(gradient, user) else None,
        "gradient_hidden": gradient is not None and not is_visible(gradient, user),
        "conductivity": conductivity if is_visible(conductivity, user) else None,
        "conductivity_hidden": conductivity is not None
        and not is_visible(conductivity, user),
        "corrections": list(child.corrections.all()),
        "parent": parent if is_visible(parent, user) else None,
        "parent_hidden": parent is not None and not is_visible(parent, user),
        "stale": is_stale(child),
    }


def source_context(measurement, user):
    """Gather the children that use a gradient or a conductivity."""
    return {
        **measured_on(measurement, user),
        "children": child_rows(measurement.heat_flow_children.order_by("pk"), user),
        "stale": is_stale(measurement),
    }


def parent_context(parent, user):
    """Gather a parent's children and the ones its quality rests on."""
    children = list(parent.children.order_by("-is_relevant", "pk"))
    if len(children) == 1:
        rests_on = {children[0].pk}
        basis = "single"
    else:
        rests_on = {c.pk for c in children if c.is_relevant}
        basis = "relevant" if rests_on else ("none" if children else "empty")
    for child in children:
        child.rests_on = child.pk in rests_on
    rows = child_rows(children, user)
    return {
        "children": rows,
        "rests_on": rests_on,
        "basis": basis,
        "site": parent.sample if is_visible(parent.sample, user) else None,
        "location": site_location(parent, user),
        "stale": is_stale(parent),
    }


CONTEXT = {
    HeatFlowSite: site_context,
    HeatFlowInterval: interval_context,
    HeatFlow: child_context,
    ThermalGradient: source_context,
    IntervalConductivity: source_context,
    ParentHeatFlow: parent_context,
}
