from django import forms
from django.forms import widgets
from django.forms.fields import IntegerField
from django.forms.models import ModelForm, construct_instance, model_to_dict
from django.forms.widgets import HiddenInput
from django.utils.translation import gettext as _
from formset.collection import FormCollection
from formset.fieldset import Fieldset, FieldsetMixin
from formset.renderers import bootstrap
from formset.richtext.widgets import RichTextarea
from formset.utils import FormMixin
from formset.widgets import (  # DateTimeInput,
    DateInput,
    DualSortableSelector,
    Selectize,
    SelectizeMultiple,
    UploadedFileInput,
)

# from geoluminate.contrib.project.models import Contributor, Dataset, Description, KeyDate, Project
from geoluminate.contrib.project.forms import GenericForm, SampleForm
from geoluminate.contrib.user.forms import ProfileFormNoImage
from geoluminate.contrib.user.models import Profile
from geoluminate.utils.forms import DefaultFormRenderer

from .models import HeatFlow, Interval


# ===================== FORMS =====================
class HeatFlowParentForm(FieldsetMixin, ModelForm):
    label = _("Heat Flow (Parent)")
    help_text = _("Add a new heat flow.")

    class Meta:
        model = HeatFlow
        fields = "__all__"


class HeatFlowChildForm(FieldsetMixin, ModelForm):
    label = _("Heat Flow (Child)")
    help_text = _("Add a new child heat flow.")

    class Meta:
        model = Interval
        fields = ["qc", "qc_unc", "q_method", "q_top", "q_bot", "hf_pen", "hf_probe", "hf_probeL", "probe_title"]


class ProbeSensingForm(FieldsetMixin, ModelForm):
    label = _("Probe Sensing")
    help_text = _("Probe sensing for marine heat flow measurements.")

    class Meta:
        model = Interval
        fields = ["hf_pen", "hf_probe", "hf_probeL", "probe_title"]


class MetadataAndFlagsForm(FieldsetMixin, ModelForm):
    label = _("Metadata and Flags")
    help_text = _("Metadata and flags for heat flow child measurements.")

    class Meta:
        model = Interval
        fields = ["q_tf_mech", "q_date_acquired", "q_method", "relevant_child"]


class TemperatureForm(FieldsetMixin, ModelForm):
    label = _("Temperature")
    help_text = _("Temperature for heat flow child measurements.")

    class Meta:
        model = Interval
        fields = [
            "t_grad_mean",
            "T_grad_uncertainty",
            "T_grad_mean_cor",
            "T_grad_uncertainty_cor",
            "T_method_top",
            "T_method_bottom",
            "T_shutin_top",
            "T_shutin_bottom",
            "T_correction_top",
            "T_correction_bottom",
            "T_count",
        ]


class ConductivityForm(FieldsetMixin, ModelForm):
    label = _("Conductivity")
    help_text = _("Conductivity for heat flow child measurements.")

    class Meta:
        model = Interval
        fields = [
            "tc_mean",
            "tc_uncertainty",
            "tc_source",
            "tc_method",
            "tc_saturation",
            "tc_pT_conditions",
            "tc_pT_function",
            "tc_startegy",
            "tc_count",
        ]
