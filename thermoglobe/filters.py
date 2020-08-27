from .models import Site, Conductivity, HeatFlow
from mapping.models import Sea, Country, Continent
import django_filters
from django_filters import widgets
from django import forms
from thermoglobe.widgets import RangeField, RangeWidget
from django.contrib import admin
from django.utils.translation import gettext as _
from django.db.models import Q

# class GeoModelChoiceField(forms.ChoiceField):

#     def __init__(self, model, display_field, *, empty_label="---------", **kwargs):
#         choices = model.objects.exclude(id__in=model.objects.filter(sites__isnull=True)).order_by(display_field).values_list('pk',display_field)
#         if choices.exists():
#             choices = list(choices)
#             choices.insert(0,('',empty_label))
#         super().__init__(choices=choices, **kwargs)

class GeoModelChoiceField2(forms.ChoiceField):

    def __init__(self, model, display_field, *, id='pk', empty_label="---------", **kwargs):
        # choices = list(model.objects.exclude(id__in=model.objects.filter(sites__isnull=True)).order_by(display_field).values_list(id,display_field))
        
        choices = model.region_choices
        choices.insert(0,('',empty_label))
        # print(choices)
        super().__init__(choices=choices, **kwargs)


class SiteFilter(forms.ModelForm):
    value = RangeField(
                label='Value',  
                required=False,
                help_text='Specify a range of values.',
                field=forms.FloatField(min_value=0),
                )

    longitude = RangeField(  
                required=False,
                field=forms.FloatField(min_value=-180, max_value= 180),
                )
    latitude = RangeField(  
                required=False,
                field=forms.FloatField(min_value=-90,max_value= 90,),
                )
    elevation = RangeField(  
                required=False,
                field=forms.FloatField(min_value=-12000,max_value=9000),
                )

    # continent = GeoModelChoiceField(Continent, 'name', required=False)
    # country = GeoModelChoiceField(Country, 'name', required=False)
    # # country = forms.ModelMultipleChoiceField(queryset=Country.objects.all())
    # # region = GeoModelChoiceField2(Country, 'region', id='region')
    # sea = GeoModelChoiceField(Sea, 'name', required=False)
    # sea = forms.ModelChoiceField(queryset=)

    class Meta:
        model = Site
        fields = ['value','latitude','longitude','elevation','country','continent','sea']


class HeatflowFilter(forms.ModelForm):
    # hf_corrected = forms.BooleanField(label='Corrected', required=False,initial=True)
    # hf_uncorrected = forms.BooleanField(label='Uncorrected',required=False,initial=True)

    value = RangeField(
                label='Heat Flow',  
                required=False,
                help_text='Specify a range of heat flow values.',
                field=forms.FloatField(min_value=0),
                )
    class Meta:
        model = HeatFlow
        fields = ['value']


# class HeatflowFilter(forms.Form):
#     hf_corrected = forms.BooleanField(label='Corrected', required=False,initial=True)
#     hf_uncorrected = forms.BooleanField(label='Uncorrected',required=False,initial=True)

#     heatflow = RangeField(
#                 label='Heat Flow',  
#                 required=False,
#                 help_text='Specify a range of heat flow values.',
#                 field=forms.FloatField(min_value=0),
#                 )
#     gradient = RangeField(
#                 label='Gradient',  
#                 required=False,
#                 help_text='Specify a range of temperature gradient values.',
#                 field=forms.FloatField(min_value=0),
#                 )
#     class Meta:
#         title = 'heat flow'

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

class PublicationFilter(forms.Form):
    
    reference__first_author__last_name__iexact = forms.CharField(label='Author', max_length=50, strip=True, required=False, help_text='Search by last name of author')
    reference__year = RangeField(
                label='Year',
                required=False,
                help_text='Year of publication',
                field=forms.IntegerField())

    class Meta:
        title = 'reference'

map_filter_forms = [SiteFilter,HeatflowFilter,ConductivityFilter,HeatGenFilter,TemperatureFilter,PublicationFilter]

class IsCorrectedFilter(admin.SimpleListFilter):

    title = _('has correction')

    parameter_name = 'has_correction'

    def lookups(self, request, model_admin):

        return (
            ('yes', _('Yes')),
            ('no',  _('No')),
        )

    def queryset(self, request, queryset):

        if self.value() == 'yes':
            return queryset.filter(corrections__isnull=False)

        if self.value() == 'no':
            return queryset.filter(Q(corrections__isnull=True))