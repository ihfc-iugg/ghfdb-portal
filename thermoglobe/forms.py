from django import forms
from .widgets import RangeField, RangeWidget
from reference.models import Upload
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from .models import Site
from betterforms.forms import BetterModelForm, Fieldset


# class SiteForm(forms.ModelForm):
class SiteForm(BetterModelForm):

    class Meta:
        model = Site
        exclude = ['geom','site_name']
        fieldsets = (
            Fieldset('site', (
                'latitude', 
                'longitude',
                'elevation',
                'country',
                'continent',
                'sea',
                'well_depth',
                'dip',         
                )),
            Fieldset('reported fields', (
                'surface_temp',
                'bottom_hole_temp',
                # 'outcrop_distance',
                # 'ruggedness',
                # 'sediment_thickness',
                # 'crustal_thickness',           
                )),
            Fieldset('calculated fields', (
                'seamount_distance',
                'outcrop_distance',
                'ruggedness',
                'sediment_thickness',
                'crustal_thickness'           
                )),
            Fieldset('geology', (
                'basin',
                'sub_basin',
                'tectonic_environment',
                'geological_province',
                'lithology',
                'USGS_code',           
                )),



        )


class DownloadForm(forms.Form):

    FILE_TYPES = (
            ('csv','.csv'),
            ('xls','.xls'),
            ('json','.json'),
            ('yaml','.yaml'),)
    file_type = forms.ChoiceField(widget=forms.Select(),choices=FILE_TYPES)

    latitude_from = forms.FloatField(required=False, max_value= 90, min_value=-90)
    latitude_to = forms.FloatField(required=False, max_value= 90, min_value=-90)
    longitude_from = forms.FloatField(required=False, max_value= 180, min_value=-180)
    longitude_to = forms.FloatField(required=False, max_value= 180, min_value=-18)
    heatflow_from = forms.FloatField(required=False, min_value=0)
    heatflow_to = forms.FloatField(required=False, min_value=0)


class UploadForm(forms.ModelForm):
    class Meta:
        model = Upload
        exclude = ['imported','imported_by','date_imported','date_uploaded','description']

class ContactForm(forms.Form):
    name = forms.CharField(max_length=75)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)
    captcha = ReCaptchaField(widget=ReCaptchaV3)

