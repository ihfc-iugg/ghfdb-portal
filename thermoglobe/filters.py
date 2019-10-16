from .models import Site, Conductivity
import django_filters
from django_filters import widgets
from django import forms
from thermoglobe.widgets import RangeField, RangeWidget


class SiteFilter(forms.Form):

    site_name = forms.CharField(label='Site Name', max_length=100, strip=True,required=False, help_text='Search for an individual site by name.')

    latitude = RangeField(  
                required=False,
                field=forms.FloatField(min_value=-90,max_value= 90,),
                )

    longitude = RangeField(  
                required=False,
                field=forms.FloatField(min_value=-180, max_value= 180),
                )

    elevation = RangeField(  
                required=False,
                help_text='Elevation in metres above sea level',
                field=forms.FloatField(),
                )
    # depth = RangeField(  
    #             required=False,
    #             help_text='Maximum depth in metres',
    #             field=forms.FloatField(),
    #             )

    # well_depth = RangeField(  
    #             required=False,
    #             help_text='Well depth in metres',
    #             field=forms.FloatField(),
    #             )

    sediment_thickness = forms.FloatField(label='Sed. Thickness', required=False, help_text='Thickness of overlying sediments.')

    class Meta:
        title = 'location'



class HeatflowFilter(forms.Form):
    hf_corrected = forms.BooleanField(label='Corrected', required=False,initial=True)
    hf_uncorrected = forms.BooleanField(label='Uncorrected',required=False,initial=True)
    # hf_reliability = forms.MultipleChoiceField(required=False)

    heatflow = RangeField(
                label='Heat Flow',  
                required=False,
                help_text='Specify a range of heat flow values.',
                field=forms.FloatField(min_value=0),
                )
    gradient = RangeField(
                label='Gradient',  
                required=False,
                help_text='Specify a range of temperature gradient values.',
                field=forms.FloatField(min_value=0),
                )
    class Meta:
        title = 'heat flow'

class ConductivityFilter(forms.Form):
    conductivity__value = RangeField(
                label='Conductivity',  
                required=False,
                help_text='Specify a range of thermal conductivity values',
                field=forms.FloatField(min_value=0),
                )
    conductivity__uncertainty = RangeField(
                label='Uncertainty',  
                required=False,
                help_text='Specify a range of thermal conductivity uncertainties',
                field=forms.FloatField(min_value=0),
                )
    class Meta:
        title = 'thermal conductivity'

class HeatGenFilter(forms.Form):

    heatgeneration__value = RangeField(
                label='Heat Gen.',  
                required=False,
                help_text='Specify a range of heat generation values',
                field=forms.FloatField(min_value=0),
                )
    heatgeneration__uncertainty = RangeField(
                label='Uncertainty',  
                required=False,
                help_text='Specify a range of heat generation uncertainties',
                field=forms.FloatField(min_value=0),
                )

    class Meta:
        title = 'heat generation'


class TemperatureFilter(forms.Form):

    # temperature__value = RangeField(
    #             label='Temperature',  
    #             required=False,
    #             help_text='Search all temperature values',
    #             field=forms.FloatField(min_value=0),
    #             )

    bottom_hole_temp__value = RangeField(
                label='Bottom Hole',  
                required=False,
                help_text='Search temperatures at bottom of only',
                field=forms.FloatField(min_value=0),
                )

    top_hole_temp__value = RangeField(
                label='Top Hole',  
                required=False,
                help_text='Search temperatures at top of hole only',
                field=forms.FloatField(min_value=0),
                )

    class Meta:
        title = 'temperature'

class ReferenceFilter(forms.Form):
    
    reference__first_author__last_name__iexact = forms.CharField(label='Author', max_length=50, strip=True, required=False, help_text='Search by last name of author')
    reference__year = RangeField(
                label='Year',
                required=False,
                help_text='Year of publication',
                field=forms.IntegerField())

    class Meta:
        title = 'reference'


map_filter_forms = [SiteFilter,HeatflowFilter,ConductivityFilter,HeatGenFilter,TemperatureFilter,ReferenceFilter]

