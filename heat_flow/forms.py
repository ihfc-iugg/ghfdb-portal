from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms

from .models import HeatFlowSite


# ===================== FORMS =====================
class HeatFlowSiteForm(forms.ModelForm):
    class Meta:
        model = HeatFlowSite
        fields = ["name", "internal_id", "dataset", "environment", "explo_method", "explo_purpose"]
        # widgets = {
        #     "length": forms.NumberInput(),
        # }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            "name",
            "internal_id",
            "dataset",
            "environment",
            "explo_method",
            "explo_purpose",
        )


# class HeatFlowParentForm(forms.ModelForm):
#     label = _("Heat Flow (Parent)")
#     help_text = _("Add a new heat flow.")

#     class Meta:
#         model = ParentHeatFlow
#         fields = "__all__"

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.layout = Layout(
#             "sample",
#             "value",
#             "uncertainty",
#             "corr_HP_flag",
#         )


# class ChildHeatFlowForm(forms.ModelForm):
#     label = _("Heat Flow (Child)")
#     help_text = _("Add a new child heat flow.")

#     class Meta:
#         model = ChildHeatFlow
#         fields = [
#             "qc",
#             "qc_uncertainty",
#             "q_method",
#             "q_top",
#             "q_bottom",
#             "hf_pen",
#             "probe_type",
#             "hf_probeL",
#             "probe_title",
#         ]


# class ProbeSensingForm(forms.ModelForm):
#     label = _("Probe Sensing")
#     help_text = _("Probe sensing for marine heat flow measurements.")

#     class Meta:
#         model = ChildHeatFlow
#         fields = ["hf_pen", "probe_type", "hf_probeL", "probe_title"]


# class MetadataAndFlagsForm(forms.ModelForm):
#     label = _("Metadata and Flags")
#     help_text = _("Metadata and flags for heat flow child measurements.")

#     class Meta:
#         model = ChildHeatFlow
#         fields = ["q_method", "relevant_child"]


# class TemperatureForm(forms.ModelForm):
#     label = _("Temperature")
#     help_text = _("Temperature for heat flow child measurements.")

#     # T_corr_top and T_corr_bottom applicable only if gradient corection for borehole effects is reported - see spreadsheet

#     # tc_location = [literature/unspecified] only if {tc_source} = [Assumed from literature]

#     class Meta:
#         model = ChildHeatFlow
#         fields = [
#             "t_grad_mean",
#             "T_grad_uncertainty",
#             "T_grad_mean_cor",
#             "T_grad_uncertainty_cor",
#             "T_method_top",
#             "T_method_bottom",
#             "T_shutin_top",
#             "T_shutin_bottom",
#             "T_corr_top",
#             "T_corr_bottom",
#             "T_count",
#         ]


# class ConductivityForm(forms.ModelForm):
#     label = _("Conductivity")
#     help_text = _("Conductivity for heat flow child measurements.")

#     class Meta:
#         model = ChildHeatFlow
#         fields = [
#             "tc_mean",
#             "tc_uncertainty",
#             "tc_source",
#             "tc_method",
#             "tc_saturation",
#             "tc_pT_conditions",
#             "tc_pT_function",
#             "tc_startegy",
#             "tc_count",
#         ]
