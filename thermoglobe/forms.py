from django import forms
from .widgets import RangeField, RangeWidget
from publications.models import Upload
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from . import models, choices
from betterforms.forms import BetterModelForm, Fieldset
from betterforms.multiform import MultiForm, MultiModelForm
from mapping import forms as map_forms


class SiteForm(BetterModelForm):

    class Meta:
        model = models.Site
        fields = choices.SITE_FIELDS

class HeatFlowForm(BetterModelForm):
    class Meta:
        model = models.HeatFlow
        fields = [            
            'depth_min',
            'depth_max',
            'tilt',
            'reliability',

            'heat_flow_corrected',
            # 'corrected_uncertainty',
            # 'uncorrected',
            # 'uncorrected_uncertainty',
            'number_of_temperatures',

            'conductivity',
            'conductivity_uncertainty',
            'number_of_conductivities',
            'conductivity_method',
            ]

# class GradientForm(BetterModelForm):
#     class Meta:
#         model = models.ThermalGradient
#         fields = [            
#             'depth_min',
#             'depth_max',
#             # 'corrected',
#             # 'corrected_uncertainty',
#             # 'uncorrected',
#             # 'uncorrected_uncertainty',
#             'number_of_temperatures',

#             ]

class CorrectionForm(BetterModelForm):
    class Meta:
        model = models.Correction
        fields = [            
            'climate',
            'topographic',
            'refraction',
            'fluid',
            'bottom_water_variation',
            'compaction',
            'other',
            'other_type',
            ]

class ConductivityForm(BetterModelForm):
    class Meta:
        model = models.Conductivity
        fields = choices.CONDUCTIVITY_FIELDS

class HeatGenForm(BetterModelForm):

    class Meta:
        model = models.HeatGeneration
        fields = choices.HEAT_GEN_FIELDS

class TemperatureForm(BetterModelForm):

    class Meta:
        model = models.Temperature
        fields = choices.TEMPERATURE_FIELDS

class BetterSiteForm(BetterModelForm):
    class Meta:
        model = models.Site
        exclude = ['geom',]
        fieldsets = (
            Fieldset('reported fields', (
                'site_name',
                'latitude', 
                'longitude',
                'elevation',
                'well_depth',
            #     )),
            # Fieldset('reported fields', (
                'surface_temp',
                'bottom_hole_temp',
                'lithology',    
                )),
            Fieldset('calculated fields', (
                'country',
                'continent',
                'sea',
                'CGG_basin',
                'seamount_distance',
                'outcrop_distance',
                'ruggedness',
                'sediment_thickness',
                'crustal_thickness'           
                )),
        )

class UploadForm(forms.ModelForm):

    # bibtex = forms.CharField(required=False, widget=forms.Textarea)

    class Meta:
        model = Upload
        exclude = ['imported','imported_by','date_imported','date_uploaded','description']

class ConfirmUploadForm(forms.ModelForm):
    class Meta:
        model = Upload
        exclude = ['imported','imported_by','date_imported','date_uploaded','description']

class SiteMultiForm(MultiModelForm):
    form_classes = {
        'site': BetterSiteForm,
        'country': map_forms.Country,
    }
