from . import models
from django import forms
import os
from django.utils.translation import gettext_lazy as _

class ImportForm(forms.Form):
    import_file = forms.FileField(
        label=_('File to import')
        )

class ConfirmImportForm(forms.Form):
    import_file_name = forms.CharField(widget=forms.HiddenInput())
    original_file_name = forms.CharField(widget=forms.HiddenInput())

    def clean_import_file_name(self):
        data = self.cleaned_data['import_file_name']
        data = os.path.basename(data)
        return data

class CountryForm(forms.ModelForm):

    class Meta:
        model = models.Country
        fields = ['name','region','subregion']

class ContinentForm(forms.ModelForm):
    class Meta:
        model = models.Continent
        fields = ['name']

class SeaForm(forms.ModelForm):
    class Meta:
        model = models.Sea
        fields = ['name']

class ProvinceForm(forms.ModelForm):
    help_text = 'These fields are calculated using the GIS shapefile produced by Hasterok (2020). The information may differ from similar fields calculated using other means. Please see the FAQ page for more info.'
    class Meta:
        model = models.Province
        exclude = ['id','poly','comments','continent','reference','area_km2','source_id']

