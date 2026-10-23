"""The GHFDB parent table (FS-012 sketch)."""

import django_tables2 as tables
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext
from heat_flow import vocabularies

from .models import GHFDBParent

#: What an empty cell shows: a dash, read out as "Not recorded".
NOT_RECORDED = mark_safe(  # noqa: S308 - fixed markup, no user input
    '<span aria-hidden="true">—</span>'
    '<span class="sr-only">{}</span>'.format(_("Not recorded"))
)


class NumberColumn(tables.Column):
    """A right-aligned number column in tabular figures."""

    def __init__(self, *args, places=None, unit=None, **kwargs):
        attrs = {
            "th": {"class": "text-end", **({"title": unit} if unit else {})},
            "td": {"class": "text-end tabular-nums whitespace-nowrap"},
        }
        super().__init__(*args, attrs=attrs, **kwargs)
        self.places = places

    def render(self, value):
        magnitude = getattr(value, "magnitude", value)
        if self.places is None:
            return f"{magnitude:g}"
        return f"{magnitude:.{self.places}f}"


class TermColumn(tables.Column):
    """A vocabulary-backed column, shown as the term's label."""

    def __init__(self, vocabulary, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vocabulary = vocabulary

    def render(self, value):
        label = getattr(value, "label", None)
        return label or dict(self.vocabulary().choices).get(str(value), value)


class GHFDBParentTable(tables.Table):
    """One row per parent, in the published GHFDB columns."""

    ID_parent = tables.Column(
        verbose_name="ID_parent",
        attrs={"td": {"class": "tabular-nums whitespace-nowrap"}},
    )
    q = NumberColumn(verbose_name="q", unit="mW/m²", places=1)
    q_uncertainty = NumberColumn(
        verbose_name="q_uncertainty", unit="mW/m²", places=1
    )
    children = tables.Column(
        verbose_name="children",
        accessor="total_children",
        attrs={
            "th": {
                "class": "text-end",
                "title": _("Number of children, with those marked relevant in brackets"),
            },
            "td": {"class": "text-end whitespace-nowrap"},
        },
    )
    name = tables.Column(
        verbose_name="name",
        accessor="site_name",
        attrs={"td": {"class": "min-w-52"}},
    )
    lat_NS = NumberColumn(verbose_name="lat_NS", unit="°", places=5)
    long_EW = NumberColumn(verbose_name="long_EW", unit="°", places=5)
    elevation = NumberColumn(verbose_name="elevation", unit="m")
    environment = TermColumn(
        vocabularies.GeographicEnvironment, verbose_name="environment"
    )
    explo_method = TermColumn(
        vocabularies.ExplorationMethod, verbose_name="explo_method"
    )
    explo_purpose = tables.Column(
        verbose_name="explo_purpose",
        accessor="sample__heatflowsite__explo_purpose",
        orderable=False,
    )
    total_depth_MD = NumberColumn(verbose_name="total_depth_MD", unit="m")
    total_depth_TVD = NumberColumn(verbose_name="total_depth_TVD", unit="m")
    corr_HP_flag = tables.BooleanColumn(
        verbose_name="corr_HP_flag",
        yesno=(_("Yes"), _("No")),
        null=True,
    )
    quality_parent = tables.Column(verbose_name="quality_parent")
    p_comment = tables.Column(
        verbose_name="p_comment",
        orderable=False,
        attrs={"td": {"class": "min-w-52 max-w-md"}},
    )

    class Meta:
        model = GHFDBParent
        fields = []
        row_headers = ["ID_parent"]
        order_by = ("ID_parent",)
        attrs = {"thead": {"th": {"class": "whitespace-nowrap"}}}

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("default", NOT_RECORDED)
        super().__init__(*args, **kwargs)

    def render_ID_parent(self, value, record):
        return format_html(
            '<a class="link link-hover" href="{}">{}</a>',
            record.get_absolute_url(),
            value,
        )

    def render_name(self, value, record):
        return format_html(
            '<a class="link link-hover" href="{}">{}</a>',
            record.sample.get_absolute_url(),
            value,
        )

    def render_children(self, value, record):
        url = reverse("ghfdb-parent-children", args=[record.ghfdb_id])
        return format_html(
            '<button type="button" class="btn btn-ghost btn-xs tabular-nums"'
            ' hx-get="{}" hx-target="#children-window" hx-swap="innerHTML"'
            ' aria-haspopup="dialog"'
            ' aria-label="{}">{} <span class="text-base-content/60">({})</span>'
            "</button>",
            url,
            ngettext(
                "Show the %(n)s child of parent %(id)s",
                "Show the %(n)s children of parent %(id)s",
                value,
            )
            % {"n": value, "id": record.ghfdb_id},
            value,
            record.relevant_children,
        )

    def render_explo_purpose(self, value, record):
        terms = [term.label for term in value.all()]
        return "; ".join(terms) if terms else NOT_RECORDED

    def render_quality_parent(self, value):
        return render_to_string("cotton/heat_flow/code.html", {"code": value})

    def order_children(self, queryset, is_descending):
        order = "-total_children" if is_descending else "total_children"
        return queryset.order_by(order, "ghfdb_id"), True

    def order_name(self, queryset, is_descending):
        order = "-site_name" if is_descending else "site_name"
        return queryset.order_by(order, "ghfdb_id"), True
