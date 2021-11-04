from django import forms
from . import models, import_choices as choices
from betterforms.forms import BetterModelForm
from betterforms.multiform import  MultiModelForm
from mapping import forms as map_forms

class DownloadForm(forms.Form):
    download_type = forms.ChoiceField(
        label="Download Type",
        help_text='The level of detail required in the downloaded files. Higher levels will result in larger download sizes.',
        required=True,
        choices=[
            ('basic','Basic'),
            ('standard','Standard'),
            ('detailed','Detailed'),
        ]
    )
    # your_name = forms.CharField(label='Your name', max_length=100)
    data_select = forms.MultipleChoiceField(
        label='Data Select',
        help_text='Select one or more of the data types below. Download will contain a csv file for each selected data type.',
        required=True,
        choices=[
            ('intervals','Heat Flow/Gradient'),
            # ('gradient','Thermal Gradient'),
            ('temperature','Temperature'),
            ('conductivity','Thermal Conductivity'),
            ('heatproduction','heat production'),
        ],
        # widget=forms.CheckboxSelectMultiple,
        widget=forms.SelectMultiple(attrs=dict(
            style="height: 100%",
         ))
    )
    class Meta:
        fields = ['download_type','data_select']

class SiteForm(BetterModelForm):

    class Meta:
        model = models.Site
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
            'bwv',
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
    heat_production = forms.FloatField(required=True,)

    class Meta:
        model = models.HeatProduction
        fields = choices.HEAT_GEN_FIELDS

class TemperatureForm(BetterModelForm):
    temperature = forms.FloatField(required=True,)

    class Meta:
        model = models.Temperature
        fields = choices.TEMPERATURE_FIELDS

class SiteMultiForm(MultiModelForm):
    form_classes = {
        'Site': SiteForm,
        'Country': map_forms.CountryForm,
        'Sea': map_forms.SeaForm,
        'Geological Province': map_forms.ProvinceForm,
    }
