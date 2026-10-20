"""The forms a researcher corrects heat flow records with (FS-009).

Each form groups its fields the way the upload template orders its columns, so a researcher who
filled the template in finds the same things in the same order.
"""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Fieldset, Layout
from django import forms
from django.forms.models import fields_for_model
from django.utils.translation import gettext_lazy as _
from fairdm.core.measurement.forms import MeasurementFormMixin
from fairdm.core.sample.forms import SampleFormMixin
from fairdm.utils.location.forms import LocationField

from .models import (
    HeatFlow,
    HeatFlowInterval,
    HeatFlowSite,
    IntervalConductivity,
    ParentHeatFlow,
    ThermalGradient,
)
from .models.child import HeatFlowCorrection, ProbeMetadata


class SectionedForm:
    """Draw a model form in titled groups, in the order ``sections`` lists them.

    Listed first among a form's bases, so the layout is built after every other base has
    added or replaced its fields.

    Attributes:
        sections: ``(heading, rows)`` pairs in page order. A row is a field name, or a tuple of
            names drawn side by side on a wide screen. The first group has no heading.
    """

    sections: tuple = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = self.get_layout()

    def get_layout(self):
        """Group the fields under the headings ``sections`` names."""
        placed: set[str] = set()
        drawn = []
        for heading, rows in self.sections:
            drawn.extend(self.get_section(heading, rows, placed))
        drawn.extend(name for name in self.fields if name not in placed)
        return Layout(*drawn)

    def get_section(self, heading, rows, placed):
        """Build one group from the fields the form carries."""
        drawn = []
        for row in rows:
            names = [row] if isinstance(row, str) else list(row)
            names = [name for name in names if name in self.fields]
            placed.update(names)
            if len(names) > 1:
                drawn.append(
                    Div(*names, css_class="grid grid-cols-1 md:grid-cols-2 gap-x-6")
                )
            else:
                drawn.extend(names)
        if not drawn or heading is None:
            return drawn
        return [Fieldset(heading, *drawn)]


class HeatFlowSiteForm(SectionedForm, SampleFormMixin, forms.ModelForm):
    """A heat flow site: where it is, the borehole, why it was drilled and its region."""

    sections = (
        (None, ["name"]),
        (
            _("Location"),
            ["location", ("elevation", "elevation_datum"), "environment"],
        ),
        (_("Borehole"), [("length", "vertical_depth"), ("azimuth", "inclination")]),
        (_("Exploration"), [("explo_method", "explo_purpose")]),
        (_("Rock"), ["lithology", "age", "stratigraphy"]),
        (_("Region"), [("country", "region"), ("continent", "domain")]),
    )

    class Meta:
        model = HeatFlowSite
        fields = [
            "name",
            "location",
            "elevation",
            "elevation_datum",
            "environment",
            "length",
            "vertical_depth",
            "azimuth",
            "inclination",
            "explo_method",
            "explo_purpose",
            "lithology",
            "age",
            "stratigraphy",
            "country",
            "region",
            "continent",
            "domain",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current = self.fields["location"]
        self.fields["location"] = LocationField(
            full=False, label=_("Coordinates"), help_text=current.help_text
        )


class HeatFlowIntervalForm(SectionedForm, SampleFormMixin, forms.ModelForm):
    """A depth interval, with the marine probe it was measured with when there was one."""

    PROBE_FIELDS = ("penetration", "probe_type", "length", "tilt")

    sections = (
        (None, [("top", "bottom"), ("vertical_depth", "vertical_datum")]),
        (
            _("Marine probe"),
            [("probe_penetration", "probe_type"), ("probe_length", "probe_tilt")],
        ),
        (_("Rock"), ["lithology", "age", "stratigraphy"]),
    )

    class Meta:
        model = HeatFlowInterval
        fields = [
            "top",
            "bottom",
            "vertical_depth",
            "vertical_datum",
            "lithology",
            "age",
            "stratigraphy",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        probe = getattr(self.instance, "probe_metadata", None)
        for name, field in fields_for_model(
            ProbeMetadata, fields=self.PROBE_FIELDS
        ).items():
            key = name if name.startswith("probe_") else f"probe_{name}"
            field.required = False
            if probe is not None:
                value = getattr(probe, name)
                field.initial = list(value.all()) if name == "probe_type" else value
            self.fields[key] = field
        self.helper.layout = self.get_layout()

    def save(self, commit=True):
        """Save the interval, and its probe metadata when any was entered."""
        interval = super().save(commit=commit)
        values = {
            name: self.cleaned_data.get(
                name if name.startswith("probe_") else f"probe_{name}"
            )
            for name in self.PROBE_FIELDS
        }
        probe = getattr(interval, "probe_metadata", None)
        if probe is None and not any(values.values()):
            return interval
        if probe is None:
            probe = ProbeMetadata(interval=interval)
        for name in ("penetration", "length", "tilt"):
            setattr(probe, name, values[name])
        probe.save()
        probe.probe_type.set(values["probe_type"] or [])
        return interval


class HeatFlowForm(SectionedForm, MeasurementFormMixin, forms.ModelForm):
    """A child heat flow, its nine corrections and the measurements it was calculated from."""

    sections = (
        (None, [("value", "uncertainty"), "method", "c_comment"]),
        (
            _("Corrections"),
            [
                (f"correction_{code}", f"correction_{code}_comment")
                for code in HeatFlowCorrection.CorrectionTypeChoices.values
            ],
        ),
        (_("Acquisition"), ["expedition", "surface_temperature", "date_acquired"]),
        (_("Calculated from"), ["thermal_gradient", "thermal_conductivity"]),
    )

    class Meta:
        model = HeatFlow
        fields = [
            "value",
            "uncertainty",
            "method",
            "c_comment",
            "expedition",
            "surface_temperature",
            "date_acquired",
            "thermal_gradient",
            "thermal_conductivity",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        interval = self.instance.sample_id
        self.fields["thermal_gradient"].queryset = ThermalGradient.objects.filter(
            sample_id=interval
        )
        self.fields[
            "thermal_conductivity"
        ].queryset = IntervalConductivity.objects.filter(sample_id=interval)
        stored = {}
        if self.instance.pk:
            stored = {c.correction_type: c for c in self.instance.corrections.all()}
        labels = dict(HeatFlowCorrection.StatusChoices.choices)
        for code, label in HeatFlowCorrection.CorrectionTypeChoices.choices:
            valid = HeatFlowCorrection.VALID_STATUS_FOR_TYPE.get(
                code, HeatFlowCorrection.ENVIRONMENTAL_VALID
            )
            correction = stored.get(code)
            self.fields[f"correction_{code}"] = forms.ChoiceField(
                label=label,
                choices=[
                    (value, labels[value])
                    for value in HeatFlowCorrection.StatusChoices.values
                    if value in valid
                ],
                initial=correction.status if correction else "-",
                required=False,
            )
            self.fields[f"correction_{code}_comment"] = forms.CharField(
                label=_("Comment"),
                initial=correction.comment if correction else "",
                required=False,
            )
        self.helper.layout = self.get_layout()

    def save(self, commit=True):
        """Save the child, then each correction that was set or already stored."""
        child = super().save(commit=commit)
        for code in HeatFlowCorrection.CorrectionTypeChoices.values:
            status = self.cleaned_data.get(f"correction_{code}") or "-"
            comment = self.cleaned_data.get(f"correction_{code}_comment") or ""
            stored = child.corrections.filter(correction_type=code).first()
            if stored is None and status == "-" and not comment:
                continue
            if stored is None:
                stored = HeatFlowCorrection(heat_flow=child, correction_type=code)
            stored.status, stored.comment = status, comment or None
            stored.save()
        return child


class ThermalGradientForm(SectionedForm, MeasurementFormMixin, forms.ModelForm):
    """A thermal gradient, measured and corrected, and the temperatures it rests on."""

    sections = (
        (
            None,
            [("value", "uncertainty"), ("corrected_value", "corrected_uncertainty")],
        ),
        (
            _("Temperature measurements"),
            [
                ("method_top", "method_bottom"),
                ("shutin_top", "shutin_bottom"),
                ("correction_top", "correction_bottom"),
                "number",
            ],
        ),
    )

    class Meta:
        model = ThermalGradient
        fields = [
            "value",
            "uncertainty",
            "corrected_value",
            "corrected_uncertainty",
            "method_top",
            "method_bottom",
            "shutin_top",
            "shutin_bottom",
            "correction_top",
            "correction_bottom",
            "number",
        ]


class IntervalConductivityForm(SectionedForm, MeasurementFormMixin, forms.ModelForm):
    """An interval conductivity: where its samples came from, how they were measured, averaged."""

    sections = (
        (None, [("value", "uncertainty")]),
        (_("Samples"), [("source", "conductivity_location")]),
        (
            _("Measurement"),
            [("method", "saturation"), ("pT_conditions", "pT_function")],
        ),
        (_("Averaging"), [("number", "strategy")]),
    )

    class Meta:
        model = IntervalConductivity
        fields = [
            "value",
            "uncertainty",
            "source",
            "conductivity_location",
            "method",
            "saturation",
            "pT_conditions",
            "pT_function",
            "number",
            "strategy",
        ]


class ChildChoiceField(forms.ModelMultipleChoiceField):
    """The children at a site, each named by its value and its depth interval."""

    def label_from_instance(self, obj):
        """Name a child by its heat flow and the interval it was measured over."""
        interval = obj.sample.get_real_instance()
        return _("%(value)s, %(top)s to %(bottom)s") % {
            "value": obj.value,
            "top": interval.top,
            "bottom": interval.bottom,
        }


class ParentHeatFlowForm(SectionedForm, MeasurementFormMixin, forms.ModelForm):
    """A site's parent heat flow, and the children at the site it rests on."""

    relevant_children = ChildChoiceField(
        queryset=HeatFlow.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label=_("Children this value rests on"),
        help_text=_(
            "The child heat flows at this site that the parent value is drawn from."
        ),
    )

    sections = (
        (
            None,
            [("value", "uncertainty"), "comment", "corr_HP_flag", "relevant_children"],
        ),
    )

    class Meta:
        model = ParentHeatFlow
        fields = ["value", "uncertainty", "comment", "corr_HP_flag"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        children = HeatFlow.objects.filter(
            sample__heatflowinterval__site_id=self.instance.sample_id
        ).order_by("sample__heatflowinterval__top", "pk")
        self.fields["relevant_children"].queryset = children
        self.fields["relevant_children"].initial = children.filter(is_relevant=True)

    def save(self, commit=True):
        """Save the parent, then mark exactly the chosen children relevant."""
        parent = super().save(commit=commit)
        chosen = set(
            self.cleaned_data["relevant_children"].values_list("pk", flat=True)
        )
        for child in self.fields["relevant_children"].queryset:
            relevant = child.pk in chosen
            if child.is_relevant != relevant:
                child.is_relevant = relevant
                child.save()
        return parent
