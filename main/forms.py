from django import forms
from main.widgets import RangeField, RangeWidget
from reference.models import FileStorage

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
        model = FileStorage
        fields = ['first_name','last_name','description','data',]
