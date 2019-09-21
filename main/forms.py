from django import forms
from main.widgets import RangeField, RangeWidget
from reference.models import FileStorage
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3

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

class UploadForm(forms.Form):

    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=75)
    email = forms.EmailField(max_length=100)
    description = forms.CharField(widget=forms.Textarea(),help_text='Please provide a brief description of the file...',)
    bibtex = forms.CharField(help_text='Paste a .bib file here',)
    captcha = ReCaptchaField(widget=ReCaptchaV3)
    data = forms.FileField()
                            
class ContactForm(forms.Form):
    name = forms.CharField(max_length=75)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)
    captcha = ReCaptchaField(widget=ReCaptchaV3)
