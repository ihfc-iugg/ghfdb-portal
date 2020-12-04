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
            ('interval','Heat Flow/Gradient'),
            # ('gradient','Thermal Gradient'),
            ('temperature','Temperature'),
            ('conductivity','Thermal Conductivity'),
            ('heatgeneration','Heat Generation'),
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
    heat_generation = forms.FloatField(required=True,)

    class Meta:
        model = models.HeatGeneration
        fields = choices.HEAT_GEN_FIELDS

class TemperatureForm(BetterModelForm):
    temperature = forms.FloatField(required=True,)

    class Meta:
        model = models.Temperature
        fields = choices.TEMPERATURE_FIELDS

class UploadForm(forms.ModelForm):

    bibtex = forms.CharField(required=False, widget=forms.Textarea)
    captcha = ReCaptchaField(widget=ReCaptchaV3)

    class Meta:
        model = models.Upload
        exclude = ['imported','imported_by','date_imported','date_uploaded','description']

    def __init__(self, *args, **kwargs):
        from django.forms.widgets import HiddenInput
        hidden = kwargs.pop('hidden',None)
        super().__init__(*args, **kwargs)
        if hidden:
            for key, field in self.fields.items():
                field.widget = HiddenInput()
            # self.fields['fieldname'].widget
            # self.fields['fieldname'].widget = HiddenInput()

class ConfirmUploadForm(forms.ModelForm):

    bibtex = forms.CharField(required=False, widget=forms.Textarea)

    class Meta:
        model = models.Upload
        exclude = ['imported','imported_by','date_imported','date_uploaded','description']


class SiteMultiForm(MultiModelForm):
    form_classes = {
        'Site': SiteForm,
        'Country': map_forms.CountryForm,
        'Sea': map_forms.SeaForm,
        'Geological Province': map_forms.ProvinceForm,
        'CGG Basins and Plays': map_forms.BasinForm,
    }
