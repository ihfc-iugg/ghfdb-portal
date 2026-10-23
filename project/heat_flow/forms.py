"""The forms a researcher corrects heat flow records with (FS-009).

Each form groups its fields the way the upload template orders its columns, so a researcher who
filled the template in finds the same things in the same order.
"""

from decimal import Decimal

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Layout
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import DecimalValidator
from django.db import models
from django.forms.models import fields_for_model
from django.utils.translation import gettext_lazy as _
from fairdm.contrib.autocomplete.fields import (
    MeasurementChoiceField,
    MeasurementMultipleChoiceField,
)
from fairdm.core.measurement.forms import MeasurementFormMixin
from fairdm.core.sample.forms import SampleFormMixin
from fairdm.utils.location.forms import LocationField
from mvp_forms.layout import Fieldset, Join
from mvp_forms.widgets import TomSelectMultiple
from quantityfield.fields import DecimalQuantityField
from quantityfield.units import ureg
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
from .signals import Recalculation
from .vocabularies import resolve_term, resolve_terms


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

    def clean(self, value):
        """Resolve the text to the terms it names, or keep the stored ones."""
        value = super().clean(value)
        if self.stored is not None and value == self.as_text(self.stored):
            return self.stored
        try:
            if self.many:
                return resolve_terms(self.vocabulary, value)
            return resolve_term(self.vocabulary, value)
        except ValueError as error:
            raise forms.ValidationError(str(error), code="unknown_term") from None


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
    measured_pairs: tuple = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field, ConceptTextField) and self.instance.pk:
                stored = getattr(self.instance, name)
                field.stored = list(stored.all()) if field.many else stored
                self.initial[name] = field.as_text(field.stored)
        for value, uncertainty in self.measured_pairs:
            self.measure(value, uncertainty)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = self.get_layout()

    def save(self, commit=True):
        """Save the record, then the related rows the form stands for.

        The rows are written by ``save_related`` inside one deferred recalculation, so
        each affected score is refreshed once. With ``commit=False`` they are written when
        ``save_m2m`` is called, as Django writes many-to-many data.

        Args:
            commit: Whether to save at once.

        Returns:
            The record.
        """
        if commit:
            with Recalculation.deferred():
                record = super().save(commit=True)
                self.save_related(record)
            return record
        record = super().save(commit=False)
        save_m2m = self.save_m2m

        def save_m2m_and_related():
            with Recalculation.deferred():
                save_m2m()
                self.save_related(record)

        self.save_m2m = save_m2m_and_related
        return record

    def save_related(self, record):
        """Write the related rows the form stands for. The base form has none.

        Args:
            record: The saved record.
        """

    def measure(self, value, uncertainty):
        """Enter a value and its uncertainty as two numbers and one unit for both.

        Each quantity becomes a plain number in its base units, and a unit choice named
        ``<value>_unit`` stands for both, so the three can be drawn as one joined group.

        Args:
            value: The name of the value's quantity field.
            uncertainty: The name of its uncertainty's quantity field.
        """
        unit = self.unit_of(value)
        for name in (value, uncertainty):
            model_field = self._meta.model._meta.get_field(name)
            if isinstance(model_field, DecimalQuantityField):
                plain = models.DecimalField.formfield(
                    model_field, max_digits=None, decimal_places=None
                )
            else:
                plain = models.FloatField.formfield(model_field)
            plain.label = model_field.verbose_name.capitalize()
            plain.help_text = model_field.help_text
            self.fields[name] = plain
            stored = getattr(self.instance, name, None)
            self.initial[name] = (
                None if stored is None else stored.m_as(model_field.base_units)
            )
        model_field = self._meta.model._meta.get_field(value)
        self.fields[unit] = forms.ChoiceField(
            label=_("Unit"),
            choices=[(choice, choice) for choice in model_field.unit_choices],
        )
        self.initial[unit] = model_field.base_units

    @staticmethod
    def unit_of(value):
        """Name the unit choice that stands for a value and its uncertainty."""
        return f"{value}_unit"

    def clean(self):
        """Give each measured pair's numbers the unit chosen for both, in base units."""
        cleaned_data = super().clean()
        for value, uncertainty in self.measured_pairs:
            unit = cleaned_data.get(self.unit_of(value))
            for name in (value, uncertainty):
                number = cleaned_data.get(name)
                if number is None or unit is None:
                    continue
                try:
                    cleaned_data[name] = self.in_base_units(name, number, unit)
                except forms.ValidationError as error:
                    self.add_error(name, error)
        return cleaned_data

    def in_base_units(self, name, number, unit):
        """Return a number entered in a unit as a quantity in its field's base units.

        A number entered in the base unit is stored as entered, and refused when it has
        more places than the field keeps. A number converted from another unit is
        quantised to the field's places.

        Args:
            name: The name of the quantity field.
            number: The number entered.
            unit: The unit it was entered in.

        Returns:
            The quantity, in the field's base units.

        Raises:
            ValidationError: If a number in the base unit has more places than the
                field keeps.
        """
        model_field = self._meta.model._meta.get_field(name)
        base = model_field.base_units
        decimal = isinstance(model_field, DecimalQuantityField)
        if unit == base:
            if decimal:
                DecimalValidator(model_field.max_digits, model_field.decimal_places)(
                    number
                )
            return ureg.Quantity(number, base)
        converted = ureg.Quantity(float(number), unit).m_as(base)
        if decimal:
            step = Decimal(1).scaleb(-model_field.decimal_places)
            converted = Decimal(str(converted)).quantize(step)
        return ureg.Quantity(converted, base)

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
            if row in self.measured_pairs:
                drawn.append(self.get_measured_group(*row))
                placed.update((*row, self.unit_of(row[0])))
                continue
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

    def get_measured_group(self, value, uncertainty):
        """Draw a value, "±", its uncertainty and their one unit in a row, under one label.

        The uncertainty is named by its own label.
        """
        return Join(
            value,
            HTML("±"),
            uncertainty,
            self.unit_of(value),
            label=self.fields[value].label,
        )


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
                    field.initial = field.as_text(field.stored)
            self.fields[key] = field
        self.helper.layout = self.get_layout()

    def probe_values(self):
        """Return the probe values entered, and the probe types chosen.

        Returns:
            The values by model field name, and the probe types.
        """
        values = {
            name: self.cleaned_data.get(
                name if name.startswith("probe_") else f"probe_{name}"
            )
            for name in self.PROBE_FIELDS
        }
        return values, values.pop("probe_type")

    def clean(self):
        """Check the probe values as the probe metadata row does, against their fields."""
        cleaned_data = super().clean()
        values, probe_types = self.probe_values()
        probe = getattr(self.instance, "probe_metadata", None)
        if probe is None and all(value is None for value in values.values()):
            return cleaned_data
        probe = probe or ProbeMetadata()
        for name, value in values.items():
            setattr(probe, name, value)
        try:
            probe.full_clean(exclude=["interval"])
        except ValidationError as error:
            for name, messages in error.message_dict.items():
                self.add_error(f"probe_{name}", messages)
        return cleaned_data

    def save_related(self, record):
        """Write the interval's probe metadata, when any was entered or already stored.

        Nothing entered means every probe value is ``None`` and no probe type is chosen.
        A zero is a value.

        Args:
            record: The saved interval.
        """
        values, probe_types = self.probe_values()
        probe = getattr(record, "probe_metadata", None)
        if (
            probe is None
            and not probe_types
            and all(value is None for value in values.values())
        ):
            return
        if probe is None:
            probe = ProbeMetadata(interval=record)
        for name, value in values.items():
            setattr(probe, name, value)
        probe.save()
        probe.probe_type.set(probe_types or [])


class HeatFlowForm(SectionedForm, MeasurementFormMixin, forms.ModelForm):
    """A child heat flow, its nine corrections and the measurements it was calculated from."""

    CORRECTION_CODES = HeatFlowCorrection.CorrectionTypeChoices.values

    thermal_gradient = MeasurementChoiceField(
        type=ThermalGradient,
        scope="edit",
        required=False,
        label=_("Temperature gradient"),
        help_text=_("A temperature gradient on this child's own depth interval."),
    )
    thermal_conductivity = MeasurementChoiceField(
        type=IntervalConductivity,
        scope="edit",
        required=False,
        label=_("Thermal conductivity"),
        help_text=_("A thermal conductivity on this child's own depth interval."),
    )

    measured_pairs = (("value", "uncertainty"),)
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
        stored = {}
        if self.instance.pk:
            stored = {
                c.correction_type: c.status for c in self.instance.corrections.all()
            }
        labels = dict(HeatFlowCorrection.StatusChoices.choices)
        for code, label in HeatFlowCorrection.CorrectionTypeChoices.choices:
            valid = HeatFlowCorrection.VALID_STATUS_FOR_TYPE.get(
                code, HeatFlowCorrection.ENVIRONMENTAL_VALID
            )
            self.fields[f"correction_{code}"] = forms.ChoiceField(
                label=label,
                choices=[("", _("Unspecified"))]
                + [
                    (value, labels[value])
                    for value in HeatFlowCorrection.StatusChoices.values
                    if value in valid
                ],
                initial=stored.get(code, ""),
                required=False,
            )
        self.helper.layout = self.get_layout()

    def clean_thermal_gradient(self):
        """Refuse a gradient measured over another depth interval."""
        return self.on_own_interval(self.cleaned_data["thermal_gradient"])

    def clean_thermal_conductivity(self):
        """Refuse a conductivity measured over another depth interval."""
        return self.on_own_interval(self.cleaned_data["thermal_conductivity"])

    def on_own_interval(self, measurement):
        """Return the measurement when it was made over this child's interval.

        Args:
            measurement: The measurement chosen, or ``None``.

        Returns:
            The measurement.

        Raises:
            ValidationError: If the measurement belongs to another interval.
        """
        if measurement is not None and measurement.sample_id != self.instance.sample_id:
            raise forms.ValidationError(
                _("Choose a measurement on this child's own depth interval."),
                code="other_interval",
            )
        return measurement

    def save_related(self, record):
        """Give the child a row for each correction type, holding the status chosen.

        A stored comment is left as it is: the form does not carry it.

        Args:
            record: The saved child.
        """
        for code in self.CORRECTION_CODES:
            HeatFlowCorrection.objects.update_or_create(
                heat_flow=record,
                correction_type=code,
                defaults={"status": self.cleaned_data.get(f"correction_{code}") or ""},
            )


class ThermalGradientForm(SectionedForm, MeasurementFormMixin, forms.ModelForm):
    """A thermal gradient, measured and corrected, and the temperatures it rests on."""

    measured_pairs = (
        ("value", "uncertainty"),
        ("corrected_value", "corrected_uncertainty"),
    )
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

    measured_pairs = (("value", "uncertainty"),)
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


class ParentHeatFlowForm(SectionedForm, MeasurementFormMixin, forms.ModelForm):
    """A site's parent heat flow, and the children at the site it rests on."""

    relevant_children = MeasurementMultipleChoiceField(
        type=HeatFlow,
        scope="edit",
        required=False,
        label=_("Children this value rests on"),
        help_text=_(
            "The child heat flows at this site that the parent value is drawn from."
        ),
    )

    measured_pairs = (("value", "uncertainty"),)
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
        if self.instance.sample_id:
            self.fields["relevant_children"].initial = list(
                self.managed_children()
                .filter(is_relevant=True)
                .values_list("pk", flat=True)
            )

    def children(self):
        """Return the child heat flows at this parent's site."""
        return HeatFlow.objects.filter(
            sample__heatflowinterval__site_id=self.instance.sample_id
        )

    def managed_children(self):
        """Return the site's children that the researcher may change.

        These are the site's children among the records the choice field offers at its
        edit scope. The form marks only these, and leaves the rest as they are.
        """
        field = self["relevant_children"].field
        return self.children().filter(pk__in=field.offered().values("pk"))

    def clean_relevant_children(self):
        """Refuse a child at another site."""
        chosen = self.cleaned_data["relevant_children"]
        if chosen.exclude(pk__in=self.children().values("pk")).exists():
            raise forms.ValidationError(
                _("Choose only children at this site."), code="other_site"
            )
        return chosen

    def save_related(self, record):
        """Mark exactly the chosen children relevant, among those the researcher may change.

        Args:
            record: The saved parent.
        """
        chosen = set(
            self.cleaned_data["relevant_children"].values_list("pk", flat=True)
        )
        for child in self.managed_children():
            relevant = child.pk in chosen
            if child.is_relevant != relevant:
                child.is_relevant = relevant
                child.save()
