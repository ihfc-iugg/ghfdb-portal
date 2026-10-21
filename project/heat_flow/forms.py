"""The forms a researcher corrects heat flow records with (FS-009).

Each form groups its fields the way the upload template orders its columns, so a researcher who
filled the template in finds the same things in the same order.
"""

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Fieldset, Layout
from django import forms
from django.db import models
from django.forms.models import fields_for_model
from django.utils.translation import gettext_lazy as _
from fairdm.core.measurement.forms import MeasurementFormMixin
from fairdm.core.sample.forms import SampleFormMixin
from fairdm.utils.location.forms import LocationField
from mvp_forms.widgets import TomSelectMultiple
from research_vocabs.fields import BaseConceptField, ConceptManyToManyField

from .models import (
    HeatFlow,
    HeatFlowInterval,
    HeatFlowSite,
    IntervalConductivity,
    ParentHeatFlow,
    ThermalGradient,
)
from .models.child import HeatFlowCorrection, ProbeMetadata


class ConceptTextField(forms.CharField):
    """A vocabulary term typed as text, written as the published file writes it.

    One term is its label. Several are their labels joined by semicolons. A label or a key is
    accepted, in any case, as the importer accepts them. Text left as it was drawn keeps the
    stored value, so a term the vocabulary no longer offers survives a save.

    Args:
        model_field: The concept field the text stands for.
        **kwargs: Passed to ``CharField``.
    """

    def __init__(self, model_field, **kwargs):
        self.many = isinstance(model_field, ConceptManyToManyField)
        self.vocabulary = model_field.vocabulary
        kwargs.setdefault("required", not model_field.blank)
        kwargs.setdefault("label", model_field.verbose_name.capitalize())
        kwargs.setdefault("help_text", model_field.help_text)
        super().__init__(**kwargs)
        self.stored = None

    def as_text(self, value):
        """Write a stored term, or several, as the published file writes them."""
        if value is None or value == "":
            return ""
        if self.many:
            return "; ".join(concept.label for concept in value)
        labels = dict(self.vocabulary().choices)
        return str(labels.get(str(value), value))

    def prepare_value(self, value):
        """Draw a stored value as text, and posted text as it was posted."""
        if isinstance(value, str):
            return value
        return self.as_text(value)

    def clean(self, value):
        """Resolve the text to the terms it names, or keep the stored ones."""
        from project.ghfdb.resources.widgets import ConceptWidget, MultiConceptWidget

        value = super().clean(value)
        if self.stored is not None and value == self.as_text(self.stored):
            return self.stored
        try:
            if self.many:
                return MultiConceptWidget(self.vocabulary).clean(value)
            return ConceptWidget(self.vocabulary).clean(value)
        except ValueError as error:
            raise forms.ValidationError(str(error)) from None


def heat_flow_formfield(db_field, **kwargs):
    """Draw a vocabulary field as text and any other multiple choice as a counted control."""
    if isinstance(db_field, (BaseConceptField, ConceptManyToManyField)):
        return ConceptTextField(db_field, **kwargs)
    if isinstance(db_field, models.ManyToManyField):
        kwargs.setdefault("widget", TomSelectMultiple(counted=True))
    return db_field.formfield(**kwargs)


class SectionedForm:
    """Draw a model form in titled groups, in the order ``sections`` lists them.

    Listed first among a form's bases, so the layout is built after every other base has
    added or replaced its fields.

    Attributes:
        sections: ``(heading, rows)`` pairs in page order. A row is a field name, or a tuple of
            names drawn side by side on a wide screen. The first group has no heading.
    """

    sections: tuple = ()

    class Media:
        css = {
            "all": [
                "https://cdn.jsdelivr.net/npm/tom-select@2.5.2/dist/css/tom-select.default.min.css",
                "mvp_forms/tomselect.css",
            ]
        }
        js = [
            "https://cdn.jsdelivr.net/npm/tom-select@2.5.2/dist/js/tom-select.complete.min.js"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field, ConceptTextField) and self.instance.pk:
                stored = getattr(self.instance, name)
                field.stored = list(stored.all()) if field.many else stored
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
        formfield_callback = heat_flow_formfield
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
        formfield_callback = heat_flow_formfield
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
            ProbeMetadata,
            fields=self.PROBE_FIELDS,
            formfield_callback=heat_flow_formfield,
        ).items():
            key = name if name.startswith("probe_") else f"probe_{name}"
            field.required = False
            if probe is not None:
                value = getattr(probe, name)
                field.initial = list(value.all()) if name == "probe_type" else value
                if isinstance(field, ConceptTextField):
                    field.stored = field.initial
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

    CORRECTION_CODES = HeatFlowCorrection.CorrectionTypeChoices.values

    sections = (
        (None, [("value", "uncertainty"), "method", "c_comment"]),
        (
            _("Corrections"),
            [
                ("correction_IS", "correction_T"),
                ("correction_S", "correction_E"),
                ("correction_TOPO", "correction_PAL"),
                ("correction_SUR", "correction_CONV"),
                "correction_HR",
            ],
        ),
        (_("Acquisition"), ["expedition", "surface_temperature", "date_acquired"]),
        (_("Calculated from"), ["thermal_gradient", "thermal_conductivity"]),
    )

    class Meta:
        formfield_callback = heat_flow_formfield
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
            status = correction.status if correction else ""
            self.fields[f"correction_{code}"] = forms.ChoiceField(
                label=label,
                choices=[("", _("Unspecified"))]
                + [
                    (value, labels[value])
                    for value in HeatFlowCorrection.StatusChoices.values
                    if value in valid
                    and value != HeatFlowCorrection.StatusChoices.UNSPECIFIED
                ],
                initial=""
                if status == HeatFlowCorrection.StatusChoices.UNSPECIFIED
                else status,
                required=False,
            )
        self.helper.layout = self.get_layout()

    def save(self, commit=True):
        """Save the child, then each correction that was set or already stored.

        A stored comment is left as it is: the form does not carry it.
        """
        child = super().save(commit=commit)
        for code in self.CORRECTION_CODES:
            status = self.cleaned_data.get(f"correction_{code}") or (
                HeatFlowCorrection.StatusChoices.UNSPECIFIED
            )
            stored = child.corrections.filter(correction_type=code).first()
            if (
                stored is None
                and status == HeatFlowCorrection.StatusChoices.UNSPECIFIED
            ):
                continue
            if stored is None:
                stored = HeatFlowCorrection(heat_flow=child, correction_type=code)
            if stored.status != status:
                stored.status = status
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
        formfield_callback = heat_flow_formfield
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
        formfield_callback = heat_flow_formfield
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
        widget=TomSelectMultiple(counted=True),
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
        formfield_callback = heat_flow_formfield
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
