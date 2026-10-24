"""The GHFDB parent table (FS-012 sketch)."""

import django_tables2 as tables
from django.db.models import F, OuterRef, Subquery
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext
from django_tables2.data import TableData, TableQuerysetData
from heat_flow.models import HeatFlowSite

from .models import GHFDBParent

NOT_RECORDED = _("Not recorded")


def not_recorded():
    """Return the mark an empty cell shows: a dash, read out as "Not recorded".

    Returns:
        Markup carrying ``data-state="not-recorded"``, translated for the
        request being rendered.
    """
    return format_html(
        '<span data-state="not-recorded"><span aria-hidden="true">—</span>'
        '<span class="sr-only">{}</span></span>',
        NOT_RECORDED,
    )


class TieBrokenQuerysetData(TableQuerysetData):
    """Table data whose every ordering ends in the published identifier.

    django-tables2 orders by the chosen column's accessors alone, so rows that
    tie on it could change places between one page and the next.
    """

    def order_by(self, aliases):
        """Order as django-tables2 does, then append ``ghfdb_id`` as the tie-break."""
        super().order_by(aliases)
        self.data = self.data.order_by(*self.data.query.order_by, "ghfdb_id")


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

    def render(self, value):
        """Show the concept's label rather than its stored key."""
        return value.label()


class GHFDBParentTable(tables.Table):
    """One row per parent, in the published GHFDB columns."""

    ID_parent = tables.Column(
        verbose_name="ID_parent",
        attrs={"td": {"class": "tabular-nums whitespace-nowrap"}},
    )
    q = NumberColumn(verbose_name="q", unit="mW/m²", places=1)
    q_uncertainty = NumberColumn(verbose_name="q_uncertainty", unit="mW/m²", places=1)
    children = tables.Column(
        verbose_name="children",
        accessor="total_children",
        attrs={
            "th": {
                "class": "text-end",
                "title": _(
                    "Number of children, with those marked relevant in brackets"
                ),
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
    environment = TermColumn(verbose_name="environment")
    explo_method = TermColumn(verbose_name="explo_method")
    explo_purpose = tables.Column(
        verbose_name="explo_purpose",
        accessor="sample__heatflowsite__explo_purpose",
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
        attrs={"td": {"class": "min-w-52 max-w-md"}},
    )

    class Meta:
        model = GHFDBParent
        fields = ()
        row_headers = ("ID_parent",)
        order_by = ("ID_parent",)
        attrs = {"thead": {"th": {"class": "whitespace-nowrap"}}}

    def __init__(self, data, *args, **kwargs):
        if not isinstance(data, TableData):
            data = TieBrokenQuerysetData(data)
        kwargs.setdefault("default", not_recorded())
        super().__init__(data, *args, **kwargs)

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
        return "; ".join(terms) if terms else not_recorded()

    def render_quality_parent(self, value):
        return render_to_string("cotton/heat_flow/code.html", {"code": value})

    def order_children(self, queryset, is_descending):
        """Sort on the number of children."""
        return queryset.order_by(
            F("total_children").desc() if is_descending else F("total_children")
        ), True

    def order_name(self, queryset, is_descending):
        """Sort on the site's name."""
        return queryset.order_by(
            F("site_name").desc() if is_descending else F("site_name")
        ), True

    def order_explo_purpose(self, queryset, is_descending):
        """Sort on the alphabetically first purpose of the site.

        A subquery, because ordering through the many-valued relation would
        join the counted query and multiply its rows.
        """
        first = (
            HeatFlowSite.explo_purpose.through.objects.filter(
                heatflowsite_id=OuterRef("sample_id")
            )
            .order_by("concept__label")
            .values("concept__label")[:1]
        )
        label = F("first_purpose")
        return queryset.annotate(first_purpose=Subquery(first)).order_by(
            label.desc(nulls_last=True) if is_descending else label.asc(nulls_last=True)
        ), True
