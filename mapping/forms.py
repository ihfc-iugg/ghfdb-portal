from django import forms
from . import models
from betterforms.forms import BetterModelForm, Fieldset

class CountryForm(BetterModelForm):

    class Meta:
        model = models.Country
        fields = ['name','region','subregion']

class ContinentForm(BetterModelForm):
    class Meta:
        model = models.Continent
        fields = ['name']

class SeaForm(BetterModelForm):
    class Meta:
        model = models.Sea
        fields = ['name']

class BasinForm(BetterModelForm):
    help_text = 'These fields are calculated using the Basins and Plays shapefile produced by CGG Robertson. The information may differ from similar fields calculated using other means. Please see the FAQ page for more info.'
    class Meta:
        model = models.Basin
        exclude = ['poly','id']

class ProvinceForm(BetterModelForm):
    help_text = 'These fields are calculated using the GIS shapefile produced by Hasterok (2020). The information may differ from similar fields calculated using other means. Please see the FAQ page for more info.'
    class Meta:
        model = models.Province
        exclude = ['id','poly','comments','continent','reference','area_km2','source_id']

