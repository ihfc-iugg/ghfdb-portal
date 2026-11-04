"""Filters for the GHFDB parent table."""

import django_filters
from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from fairdm.contrib.autocomplete.fields import (
    DatasetMultipleChoiceField,
    ProjectMultipleChoiceField,
)
from fairdm.contrib.autocomplete.filters import RecordMultipleFilter
from heat_flow import vocabularies
from heat_flow.models import HeatFlowSite
from heat_flow.utils import MScoreOptions, UScoreOptions
from mvp.filters import SearchFilter
from mvp_forms.fields import LatitudeField, LongitudeField
from mvp_forms.widgets import RangeInput, TomSelectMultiple

from .models import GHFDBParent


def counted(placeholder):
    """Return a multiple choice drawn as a counted control, never the browser's own select.

    Args:
        placeholder: Text shown while nothing is chosen.

    Returns:
        A ``TomSelectMultiple`` that shows how many values are chosen.
    """
    return TomSelectMultiple(counted=True, placeholder=placeholder)


class BoundsInput(RangeInput):
    """django-mvp-forms' range as one join: a minimum, a dash, a maximum.

    The dash between the ends is drawn as the package draws text in a
    ``Join``, a framed join item. The ends are sent as ``<name>_min`` and
    ``<name>_max``, so a filtered address reads as the bounds it holds.
    """

    template_name = "ghfdb/widgets/bounds.html"

    def __init__(self, attrs=None):
        super().__init__(attrs, joined=True)
        self.widgets_names = ["_min", "_max"]

    def get_context(self, name, value, attrs):
        """Name each end inside its input, Min and Max.

        Args:
            name: The filter's name.
            value: The bounds to draw.
            attrs: HTML attributes for both ends.

        Returns:
            The widget's template context.
        """
        context = super().get_context(name, value, attrs)
        for part in context["widget"]["subwidgets"]:
            part["attrs"]["placeholder"] = part["frame_name"]
        return context


class BoundsField(django_filters.fields.RangeField):
    """A lower and an upper bound, refusing an upper bound below the lower.

    Args:
        *args: Passed to the range field.
        end_field: The form field class cleaning each bound, such as
            ``LatitudeField`` for a latitude.
        **kwargs: Passed to the range field.
    """

    def __init__(self, *args, end_field=forms.DecimalField, **kwargs):
        kwargs.setdefault("fields", (end_field(), end_field()))
        super().__init__(*args, **kwargs)

    def compress(self, data_list):
        """Join the two bounds into a slice.

        Args:
            data_list: The cleaned lower and upper bound, either of which may be None.

        Returns:
            The bounds as a slice, or None when both are empty.

        Raises:
            ValidationError: With code ``inverted`` when the upper bound is below
                the lower.
        """
        if data_list:
            low, high = data_list
            if low is not None and high is not None and high < low:
                raise forms.ValidationError(
                    _("The upper bound is below the lower bound."), code="inverted"
                )
        return super().compress(data_list)


class BoundsFilter(django_filters.RangeFilter):
    """A lower bound, an upper bound or both on one number column.

    Either side may be left empty, which leaves that side open. ``end_field``
    names the form field class cleaning each bound.
    """

    field_class = BoundsField

    def __init__(self, *args, **kwargs):
        """Draw the bounds with ``BoundsInput`` unless another widget is given."""
        kwargs.setdefault("widget", BoundsInput())
        super().__init__(*args, **kwargs)


class GHFDBParentFilter(django_filters.FilterSet):
    """Narrow the GHFDB parents by their published columns, dataset and project."""

    name = SearchFilter(fields=["sample__name"], label=_("Search site names"))

    q = BoundsFilter(field_name="value", label=_("q (mW/m²)"))
    q_uncertainty = BoundsFilter(
        field_name="uncertainty", label=_("q_uncertainty (mW/m²)")
    )
    elevation = BoundsFilter(
        field_name="sample__heatflowsite__elevation", label=_("elevation (m)")
    )
    total_depth_MD = BoundsFilter(
        field_name="sample__heatflowsite__length", label=_("total_depth_MD (m)")
    )
    total_depth_TVD = BoundsFilter(
        field_name="sample__heatflowsite__vertical_depth",
        label=_("total_depth_TVD (m)"),
    )
    lat_NS = BoundsFilter(
        field_name="lat_NS", end_field=LatitudeField, label=_("lat_NS (°)")
    )
    long_EW = BoundsFilter(
        field_name="long_EW", end_field=LongitudeField, label=_("long_EW (°)")
    )

    environment = django_filters.MultipleChoiceFilter(
        field_name="sample__heatflowsite__environment",
        label=_("environment"),
        widget=counted(_("Any environment")),
    )
    explo_method = django_filters.MultipleChoiceFilter(
        field_name="sample__heatflowsite__explo_method",
        label=_("explo_method"),
        widget=counted(_("Any method")),
    )
    explo_purpose = django_filters.MultipleChoiceFilter(
        method="filter_explo_purpose",
        label=_("explo_purpose"),
        widget=counted(_("Any purpose")),
    )
    corr_HP_flag = django_filters.MultipleChoiceFilter(
        method="filter_corr_hp",
        label=_("corr_HP_flag"),
        choices=[("yes", _("Yes")), ("no", _("No")), ("unknown", _("Not recorded"))],
    )
    U_score = django_filters.MultipleChoiceFilter(
        label=_("U-score"),
        choices=UScoreOptions.choices,
    )
    M_score = django_filters.MultipleChoiceFilter(
        label=_("M-score"),
        choices=MScoreOptions.choices,
    )
    project = RecordMultipleFilter(
        ProjectMultipleChoiceField,
        field_name="dataset__project",
        scope="view",
        label=_("Project"),
    )
    dataset = RecordMultipleFilter(
        DatasetMultipleChoiceField, field_name="dataset", scope="view"
    )

    class Meta:
        model = GHFDBParent
        fields: list[str] = []

    def __init__(self, *args, **kwargs):
        """Offer each vocabulary's terms."""
        super().__init__(*args, **kwargs)
        for name, vocabulary in (
            ("environment", vocabularies.GEOGRAPHIC_ENVIRONMENT),
            ("explo_method", vocabularies.EXPLORATION_METHOD),
            ("explo_purpose", vocabularies.EXPLORATION_PURPOSE),
        ):
            self.filters[name].extra["choices"] = vocabularies.choices(vocabulary)

    def filter_explo_purpose(self, queryset, name, value):
        """Keep parents whose site has any chosen purpose.

        The sites are a subquery so the parents gain no join: a join would
        repeat each parent per purpose and inflate its child counts.

        Args:
            queryset: The parents being filtered.
            name: The filter's name.
            value: The chosen purposes' addresses.

        Returns:
            The parents whose site has any of them.
        """
        if not value:
            return queryset
        sites = HeatFlowSite.objects.filter(explo_purpose__uri__in=value)
        return queryset.filter(sample__in=sites.values("pk"))

    def filter_corr_hp(self, queryset, name, value):
        """Keep parents whose heat production correction is any chosen state.

        Args:
            queryset: The parents being filtered.
            name: The filter's name.
            value: The chosen states: ``yes``, ``no`` or ``unknown``.

        Returns:
            The parents in any chosen state.
        """
        states = {
            "yes": Q(corr_HP_flag=True),
            "no": Q(corr_HP_flag=False),
            "unknown": Q(corr_HP_flag__isnull=True),
        }
        condition = Q()
        for chosen in value:
            condition |= states[chosen]
        return queryset.filter(condition)
