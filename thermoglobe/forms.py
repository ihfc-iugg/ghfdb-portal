from django import forms
from .widgets import RangeField, RangeWidget
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from . import models, import_choices as choices
from betterforms.forms import BetterModelForm, Fieldset
from betterforms.multiform import MultiForm, MultiModelForm
from mapping import forms as map_forms
from collections import OrderedDict

class DownloadForm(forms.Form):
    options = forms.ChoiceField(
        choices=[
            ('info', '... choose an option'),
            ('basic','Basic'),
            ('standard','Standard'),
            ('detailed','Detailed'),
        ]
    )

class SiteForm(BetterModelForm):

    class Meta:
        model = models.Site
        # fields = ['site_name','latitude','longitude']
        fields = choices.SITE_FIELDS

class HeatFlowForm(BetterModelForm):
    class Meta:
        model = models.Interval
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

            'average_conductivity',
            'conductivity_uncertainty',
            'number_of_conductivities',
            'conductivity_method',
            ]

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
    conductivity = forms.FloatField(required=True,)

    class Meta:
        model = models.Conductivity
        fields = choices.CONDUCTIVITY_FIELDS

class HeatGenForm(BetterModelForm):
    heat_generation = forms.FloatField(required=True,)

    class Meta:
        model = models.HeatGeneration
        fields = choices.HEAT_GEN_FIELDS

class TemperatureForm(BetterModelForm):
    temperature = forms.FloatField(required=True,)

    class Meta:
        model = models.Temperature
        fields = choices.TEMPERATURE_FIELDS

class BetterSiteForm(BetterModelForm):
    class Meta:
        model = models.Site
        exclude = ['geom',]
        fieldsets = (
            # Fieldset('Database ID', (
            #     'id',
            #     )),
            Fieldset('reported fields', (
                'site_name',
                'latitude', 
                'longitude',
                'elevation',
                'well_depth',
                'surface_temp',
                'bottom_hole_temp',    
                )),
            # Fieldset('calculated fields', (
            #     'country',
            #     'continent',
            #     'political',
            #     'sea',
            #     'basin',
            #     'seamount_distance',
            #     'outcrop_distance',
            #     'sediment_thickness',
            #     'crustal_thickness'           
            #     )),
        )

class UploadForm(forms.ModelForm):

    bibtex = forms.CharField(required=False, widget=forms.Textarea)

    class Meta:
        model = models.Upload
        exclude = ['imported','imported_by','date_imported','date_uploaded','description']

class ConfirmUploadForm(forms.ModelForm):
    class Meta:
        model = models.Upload
        exclude = ['imported','imported_by','date_imported','date_uploaded','description']

class SiteMultiForm(MultiModelForm):
    form_classes = OrderedDict(
        Site=SiteForm,
        Country=map_forms.CountryForm,
        Sea=map_forms.SeaForm,
    )
    form_classes['Geological Province'] = map_forms.ProvinceForm
    form_classes['CGG Basins and Plays'] = map_forms.BasinForm
