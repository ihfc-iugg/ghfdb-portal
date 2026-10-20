"""Template tags for the heat flow overview pages."""

from django import template
from django.utils.translation import get_language

from heat_flow import overview

register = template.Library()


@register.simple_tag(takes_context=True)
def heat_flow_page(context, record):
    """Return what the heat flow page of ``record`` shows beyond FairDM's shared page.

    The content is gathered the first time a render asks for ``record`` and kept in the
    render context, so a second block asking for the same record costs no query.

    Args:
        context: The template context, which carries the request.
        record: The heat flow record whose page is being rendered.

    Returns:
        The content ``HeatFlowPage.context`` gathers for the record's type.
    """
    request = context["request"]
    gathered = context.render_context.setdefault("heat_flow_page", {})
    key = (type(record), record.pk)
    if key not in gathered:
        show_all = request.GET.get("show") == "all"
        page = overview.HeatFlowPage(record, request.user, show_all=show_all)
        gathered[key] = page.context()
    return gathered[key]


@register.filter
def plus_minus(value, uncertainty):
    """Write a quantity with its uncertainty before the unit: "17.63 ± 0.91 K/km".

    Args:
        value: The quantity, or ``None``.
        uncertainty: Its uncertainty as a quantity, or ``None``.

    Returns:
        The value alone when there is no uncertainty, and an empty string when there is
        no value.
    """
    if value is None:
        return ""
    units = getattr(value, "units", None)
    text = f"{getattr(value, 'magnitude', value)}"
    if uncertainty is not None:
        text += f" ± {getattr(uncertainty, 'magnitude', uncertainty)}"
    return f"{text} {units:~P}" if units is not None else text


@register.filter
def labels(concepts):
    """Write vocabulary concepts as their labels, joined by commas.

    A graph concept is written in the active language.

    Args:
        concepts: One concept, a many-to-many manager of concepts, or ``None``.

    Returns:
        The labels joined by commas, and an empty string when there are none.
    """
    if concepts is None:
        return ""
    items = concepts.all() if hasattr(concepts, "all") else [concepts]
    language = (get_language() or "en").split("-")[0]
    names = []
    for concept in items:
        label = concept.label
        names.append(str(label(language) if callable(label) else label))
    return ", ".join(name for name in names if name)
