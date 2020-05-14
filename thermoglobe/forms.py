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

class UploadForm(forms.ModelForm):
    class Meta:
        model = Upload
        exclude = ['imported','imported_by','date_imported','date_uploaded','description']

