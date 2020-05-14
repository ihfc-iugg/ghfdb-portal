# from betterforms.forms import BaseForm
from betterforms.forms import BetterModelForm
from thermoglobe.models import Site
from .models import Reference
from django import forms


class SiteForm(BetterModelForm):

    class Meta:
        model = Site
        fieldsets = [
            ("Site Information", 
                {'fields': [
                    'site_name',
                    ('latitude','longitude','elevation'),
                    ('operator','cruise'),
                    ]}),
            ('Calculated Fields',
                {'fields': [ 
                    'seamount_distance',
                    'outcrop_distance',
                    'ruggedness',
                    'sediment_thickness',
                    'crustal_thickness']}),
            ('Reported Fields',
                {'fields': [
                    ('surface_temp','bottom_hole_temp'),
                    ('well_depth','dip',),
                    ]}),        
            ('Geology',
                {'fields': [ 
                    ('basin','sub_basin'),
                    'tectonic_environment',
                    # 'geo_province',
                    'lithology']}),
              
                    ]


# class AuthorCardForm(forms.ModelForm):

#     class Meta:
#         model=Author
#         exclude = ['id','slug']

class ReferenceForm(forms.ModelForm):

    class Meta:
        model = Reference
        fields = [
                # 'entry_type',
                'title',
                'first_author',
                'year',
                'journal',
                'is_verified',
                'abstract',
             
                    ]