# from betterforms.forms import BaseForm
from betterforms.forms import BetterModelForm
from thermoglobe.models import Site
from .models import Publication
from django import forms

class PublicationForm(forms.ModelForm):

    class Meta:
        model = Publication
        fields = [
                # 'type',
                'title',
                'authors',
                'year',
                'journal',
                'is_verified',
                'abstract',
             
                    ]