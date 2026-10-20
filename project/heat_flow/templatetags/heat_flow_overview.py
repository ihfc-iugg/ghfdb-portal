"""Template tags for the heat flow overview pages.

SKETCH: the prototype reaches its context through a tag; the plan decides the final route.
"""

from django import template

from heat_flow import overview

register = template.Library()


@register.simple_tag(takes_context=True)
def heat_flow_page(context, record):
    """Return what the heat flow page of ``record`` shows beyond FairDM's shared page."""
    request = context["request"]
    show_all = request.GET.get("intervals") == "all"
    return overview.HeatFlowPage(record, request.user, show_all=show_all).context()


@register.filter
def quantity(value, digits=None):
    """Write a quantity as its magnitude and abbreviated unit, or an empty string."""
    if value is None or value == "":
        return ""
    magnitude = getattr(value, "magnitude", value)
    units = getattr(value, "units", None)
    number = (
        f"{magnitude:.{digits}f}"
        if digits is not None
        else f"{magnitude:g}"
        if isinstance(magnitude, float)
        else f"{magnitude}"
    )
    return f"{number} {units:~P}" if units is not None else number


@register.simple_tag
def plus_minus(value, uncertainty):
    """Write a quantity with its uncertainty before the unit: "17.63 ± 0.91 K/km"."""
    if value is None:
        return ""
    units = getattr(value, "units", None)
    text = f"{getattr(value, 'magnitude', value)}"
    if uncertainty is not None:
        text += f" ± {getattr(uncertainty, 'magnitude', uncertainty)}"
    return f"{text} {units:~P}" if units is not None else text


@register.filter
def labels(concepts):
    """Write a set of vocabulary concepts as their labels, joined by commas."""
    if concepts is None:
        return ""
    items = concepts.all() if hasattr(concepts, "all") else [concepts]
    names = []
    for concept in items:
        label = getattr(concept, "label", None)
        label = label() if callable(label) else label
        names.append(str(label or concept))
    return ", ".join(names)
