from django import forms
from . import models, import_choices as choices
from mapping import forms as map_forms
from django import forms
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.layout import Layout, ButtonHolder, Submit, Field


class DownloadWithChoicesForm(forms.Form):
    download_type = forms.ChoiceField(
        label="Download Type",
        help_text='The level of detail required in the downloaded files. Higher levels will result in larger download sizes.',
        required=True,
        choices=[('basic','Basic'),
                ('standard','Standard'),
                ('detailed','Detailed')])

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'GET'
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
                Field('download_type', css_class='mb-2'),
                Field('data_select', css_class='mb-2'),
            ButtonHolder(
                Submit('submit', 'Download', css_class='button mt-2')
            )
        )

class DownloadBasicForm(forms.Form):
    download_type = forms.ChoiceField(
        label="Download Type",
        help_text='Standard: simple heat flow and thermal gradient estimates. Detailed: Includes corrected and uncorrected estimates.',
        required=False,
        choices=[   ('standard','Standard'),
                    ('detailed','Detailed')])

    class Meta:
        fields = ['download_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.form_show_labels = True
        self.helper.layout = Layout(
                Field('download_type', css_class='mb-2'),
                ButtonHolder(
                Submit('submit', 'Download', css_class='button mt-2')
            ))

class SiteForm(ModelForm):

    class Meta:
        model = models.Site
        fields = choices.SITE_FIELDS

class HeatFlowForm(ModelForm):
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

class CorrectionForm(ModelForm):
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

class ConductivityForm(ModelForm):
    conductivity = forms.FloatField(required=True,)

    class Meta:
        model = models.Conductivity
        fields = choices.CONDUCTIVITY_FIELDS

class HeatGenForm(ModelForm):
    heat_production = forms.FloatField(required=True,)

    class Meta:
        model = models.HeatProduction
        fields = choices.HEAT_GEN_FIELDS

class TemperatureForm(ModelForm):
    temperature = forms.FloatField(required=True,)

    class Meta:
        model = models.Temperature
        fields = choices.TEMPERATURE_FIELDS

class SiteMultiForm(ModelForm):
    form_classes = {
        'Site': SiteForm,
        'Country': map_forms.CountryForm,
        'Ocean': map_forms.OceanForm,
        'Geological Province': map_forms.ProvinceForm,
    }
