"""Filters for the GHFDB parent table (FS-012 sketch)."""

import django_filters
from django import forms
from django.utils.translation import gettext_lazy as _
from fairdm.core.dataset.models import Dataset
from fairdm.core.project.models import Project
from heat_flow import vocabularies
from heat_flow.utils import MScoreOptions, UScoreOptions
from mvp.filters import SearchFilter
from mvp_forms.widgets import TomSelectMultiple

from .models import GHFDBParent


def counted(placeholder):
    """A multiple choice drawn as a counted control, never the browser's own select."""
    return TomSelectMultiple(counted=True, placeholder=placeholder)


class BoundsField(django_filters.fields.RangeField):
    """Two number inputs, From and To, refusing a To below its From."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        low, high = self.widget.widgets
        low.attrs["placeholder"] = _("From")
        high.attrs["placeholder"] = _("To")

    def compress(self, data_list):
        if data_list:
            low, high = data_list
            if low is not None and high is not None and high < low:
                raise forms.ValidationError(
                    _("The upper bound is below the lower bound."), code="inverted"
                )
        return super().compress(data_list)


class BoundsFilter(django_filters.RangeFilter):
    """A lower bound, an upper bound or both on one number column.

    Either side may be left empty, which leaves that side open. Drawn as two
    inputs named ``<name>_min`` and ``<name>_max``.
    """

    field_class = BoundsField


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
    lat_NS = BoundsFilter(field_name="lat_NS", label=_("lat_NS (°)"))
    long_EW = BoundsFilter(field_name="long_EW", label=_("long_EW (°)"))

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
        field_name="sample__heatflowsite__explo_purpose__name",
        label=_("explo_purpose"),
        widget=counted(_("Any purpose")),
        distinct=True,
    )
    corr_HP_flag = django_filters.MultipleChoiceFilter(
        method="filter_corr_hp",
        label=_("corr_HP_flag"),
        choices=[("yes", _("Yes")), ("no", _("No")), ("unknown", _("Not recorded"))],
        widget=counted(_("Any")),
    )
    U_score = django_filters.MultipleChoiceFilter(
        label=_("U-score"),
        choices=UScoreOptions.choices,
        widget=counted(_("Any U-score")),
    )
    M_score = django_filters.MultipleChoiceFilter(
        label=_("M-score"),
        choices=MScoreOptions.choices,
        widget=counted(_("Any M-score")),
    )
    dataset = django_filters.ModelMultipleChoiceFilter(
        queryset=Dataset.objects.none(),
        label=_("Dataset"),
        widget=counted(_("Any dataset")),
    )
    project = django_filters.ModelMultipleChoiceFilter(
        field_name="dataset__project",
        queryset=Project.objects.none(),
        label=_("Project"),
        widget=counted(_("Any project")),
    )

    class Meta:
        model = GHFDBParent
        fields = []

    def __init__(self, *args, **kwargs):
        """Offer the vocabulary terms, and only the datasets and projects the visitor can see.

        The queryset is the parents the visitor may see, so the dataset and
        project choices are the ones those parents belong to.
        """
        super().__init__(*args, **kwargs)
        parents = self.queryset
        for name, vocabulary in (
            ("environment", vocabularies.GeographicEnvironment),
            ("explo_method", vocabularies.ExplorationMethod),
            ("explo_purpose", vocabularies.ExplorationPurpose),
        ):
            self.filters[name].extra["choices"] = vocabulary().choices
        if parents is not None:
            dataset_ids = parents.values("dataset_id")
            self.filters["dataset"].queryset = Dataset.objects.filter(
                pk__in=dataset_ids
            ).order_by("name")
            self.filters["project"].queryset = Project.objects.filter(
                datasets__in=dataset_ids
            ).distinct().order_by("name")

    def filter_corr_hp(self, queryset, name, value):
        """Keep parents whose heat production correction is any chosen state."""
        from django.db.models import Q

        states = {
            "yes": Q(corr_HP_flag=True),
            "no": Q(corr_HP_flag=False),
            "unknown": Q(corr_HP_flag__isnull=True),
        }
        condition = Q()
        for chosen in value:
            condition |= states[chosen]
        return queryset.filter(condition)
