from django import forms
from . import models
from betterforms.forms import BetterModelForm, Fieldset

class Country(BetterModelForm):

    class Meta:
        model = models.Country
        fieldsets = (
            Fieldset('country', (
                'name', 
                'region',
                'subregion',
                    )),
        )

class Continent(BetterModelForm):
    class Meta:
        model = models.Continent
        fields = ['name']

class Sea(BetterModelForm):
    class Meta:
        model = models.Sea
        fields = ['name']

class Basin(BetterModelForm):
    class Meta:
        model = models.Basin
        exclude = ['poly']


