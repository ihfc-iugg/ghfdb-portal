from django.forms.models import ModelForm
from django.utils.translation import gettext as _
from formset.fieldset import FieldsetMixin

from .models import ChildHeatFlow, ParentHeatFlow


# ===================== FORMS =====================
class HeatFlowParentForm(FieldsetMixin, ModelForm):
    label = _("Heat Flow (Parent)")
    help_text = _("Add a new heat flow.")

    class Meta:
        model = ParentHeatFlow
        fields = "__all__"


class ChildHeatFlowForm(FieldsetMixin, ModelForm):
    label = _("Heat Flow (Child)")
    help_text = _("Add a new child heat flow.")

    class Meta:
        model = ChildHeatFlow
        fields = [
            "qc",
            "qc_uncertainty",
            "q_method",
            "q_top",
            "q_bottom",
            "hf_pen",
            "probe_type",
            "hf_probeL",
            "probe_title",
        ]


class ProbeSensingForm(FieldsetMixin, ModelForm):
    label = _("Probe Sensing")
    help_text = _("Probe sensing for marine heat flow measurements.")

    class Meta:
        model = ChildHeatFlow
        fields = ["hf_pen", "probe_type", "hf_probeL", "probe_title"]


class MetadataAndFlagsForm(FieldsetMixin, ModelForm):
    label = _("Metadata and Flags")
    help_text = _("Metadata and flags for heat flow child measurements.")

    class Meta:
        model = ChildHeatFlow
        fields = ["q_method", "relevant_child"]


class TemperatureForm(FieldsetMixin, ModelForm):
    label = _("Temperature")
    help_text = _("Temperature for heat flow child measurements.")

    # T_corr_top and T_corr_bottom applicable only if gradient corection for borehole effects is reported - see spreadsheet

    # tc_location = [literature/unspecified] only if {tc_source} = [Assumed from literature]

    class Meta:
        model = ChildHeatFlow
        fields = [
            "t_grad_mean",
            "T_grad_uncertainty",
            "T_grad_mean_cor",
            "T_grad_uncertainty_cor",
            "T_method_top",
            "T_method_bottom",
            "T_shutin_top",
            "T_shutin_bottom",
            "T_corr_top",
            "T_corr_bottom",
            "T_count",
        ]


class ConductivityForm(FieldsetMixin, ModelForm):
    label = _("Conductivity")
    help_text = _("Conductivity for heat flow child measurements.")

    class Meta:
        model = ChildHeatFlow
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
