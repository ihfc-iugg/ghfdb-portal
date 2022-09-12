from database.models import Site
from mapping.models import Ocean, Country, Continent
# import django_filters as df
from django_filters import MultipleChoiceFilter, ChoiceFilter, RangeFilter
from django.contrib import admin
from django.utils.translation import gettext as _
from django.db import models
from main.forms import DownloadBasicForm
# from main.forms import DownloadBasicForm, MapFilterForm
from django.db.models.functions import Coalesce
from django_filters import rest_framework as df
from global_tectonics.models import Plate, Province
from crispy_forms.helper import FormHelper
from crispy_bootstrap5.bootstrap5 import FloatingField, BS5Accordion
from crispy_forms.layout import Layout, ButtonHolder, Row, Column, Field, HTML, Button, Div
from crispy_forms.bootstrap import AccordionGroup
from core.utils import get_choices

class MapFilter(df.FilterSet):
    name = df.CharFilter(lookup_expr='icontains', label='Site Name')
    lat_gt = df.NumberFilter(field_name='lat', lookup_expr='gt', label='Latitude')
    lat_lt = df.NumberFilter(field_name='lat', lookup_expr='lt', label='Latitude')
    lng_gt = df.NumberFilter(field_name='lng', lookup_expr='gt', label='Longitude')
    lng_lt = df.NumberFilter(field_name='lng', lookup_expr='lt', label='Longitude')
    elevation_gt = df.NumberFilter(field_name='elevation', lookup_expr='gt', label='Elevation (m)')
    elevation_lt = df.NumberFilter(field_name='elevation', lookup_expr='lt', label='Elevation (m)')
    # plate = df.ChoiceFilter(field_name='plate__plate',
    #     choices=get_choices(Plate, "plate"),
    #     lookup_expr='exact', label='Tectonic Plate')
    # crust_type = df.ChoiceFilter(field_name='plate__plate',
    #     choices=[('continental','Continental'),{'oceanic','Oceanic'}],
    #     lookup_expr='exact', label='Crust Type')
    # site = df.CharFilter(lookup_expr='icontains', label='Site Name')

    class Meta:
        model = Site
        fields = ["name", 'references', 'id']

    helper = FormHelper()
    helper.form_method = 'GET'
    helper.form_id = 'map-filter-form'
    helper.layout = Layout(
        BS5Accordion(
            AccordionGroup('Geographic',
                FloatingField('name', placeholder='Site name'),
                Row(
                    Div(FloatingField('lat_lt'), css_class='w-50'),
                    css_class='justify-content-center'
                    ),
                Row(
                    Column(FloatingField('lng_gt')),
                    Column(FloatingField('lng_lt')),
                    ),
                Row(
                    Div(FloatingField('lat_gt'), css_class='w-50'),
                    css_class='justify-content-center'
                    ),

                Row(
                    Column(FloatingField('elevation_gt')),
                    Column(FloatingField('elevation_lt')),
                    css_class='justify-content-center'
                    ),
                ),
            AccordionGroup('Geology',
                FloatingField('plate'),
                FloatingField('crust_type'),
                ),
        flush=True,
        ),
        ButtonHolder(
            Button('button', 'Search', onclick='updateMap()', css_class='button solid large'),
        )
    )
 

class Filter(df.FilterSet):

    def filter_queryset(self, queryset):
        """
        Filter the queryset with the underlying form's `cleaned_data`. You must
        call `is_valid()` or `errors` before calling this method.

        This method should be overridden if additional filtering needs to be
        applied to the queryset before it is cached.
        """
        data = self.form.cleaned_data
        del data['data_type']
        for name, value in data.items():
            queryset = self.filters[name].filter(queryset, value)
            assert isinstance(queryset, models.QuerySet), \
                "Expected '%s.%s' to return a QuerySet, but got a %s instead." \
                % (type(self).__name__, name, type(queryset).__name__)
        return queryset

class WorldMapFilter(Filter):
    
    data_type = ChoiceFilter(
        choices = [
                ('heat_flow','Heat Flow'),
                ('gradient','Thermal Gradient'),
                ('temperature','Temperature'),
                ('conductivity','Thermal Conductivity'),
                ('heat_production','heat production'),],
        )

    # value = RangeFilter(
    #             label='Value',  
    #             help_text='Specify a range of values.',
    #             # field=forms.FloatField(min_value=0),
    #             )

    lng = RangeFilter()
    lat = RangeFilter()
    elevation = RangeFilter()

    continent = MultipleChoiceFilter(
            choices=Continent.objects.exclude(sites__isnull=True).values_list('id','name').order_by('name'),
            lookup_expr='exact',
        )

    # country = ModelMultipleChoiceFilter(
    country = MultipleChoiceFilter(
            choices=Country.objects.exclude(sites__isnull=True).values_list('id','name').order_by('name'),
            lookup_expr='exact',
        )

    ocean = MultipleChoiceFilter(
            lookup_expr='exact',
            choices = Ocean.objects.exclude(sites__isnull=True).values_list('id','name').order_by('name'),
        )

    province = MultipleChoiceFilter(
            choices=Province.objects.exclude(sites__isnull=True).values_list('id','name').order_by('name'),
            lookup_expr='exact',
        )

    tectonic_environment = MultipleChoiceFilter(
            choices = Province.objects.exclude(sites__isnull=True).values_list('type','type').distinct(),
            field_name='province__type',
            lookup_expr='exact',
            label='Tectonic Environment'
        )

    # This is so i can include the download form as part of the map filter
    download_form = DownloadBasicForm()

    class Meta:
        model = Site
        fields = ['lat','lng','elevation','country','continent','ocean','province']

class EmptySites(admin.SimpleListFilter):

    title = _('is empty')
    parameter_name = 'is_empty'

    def lookups(self, request, model_admin):

        return (
            (True, _('Empty')),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                intervals__isnull=True, 
                temperature__isnull=True,
                conductivity__isnull=True,
                heat_production__isnull=True,
                )

class EmptyPublications(admin.SimpleListFilter):

    title = _('data type')
    parameter_name = 'data_type'

    def lookups(self, request, model_admin):

        return (
            ("has_heat_flow", _('Has heat flow')),
            ("has_gradient", _('Has gradient')),
            ("has_temperature", _('Has temperature')),
            ("has_conductivity", _('Has conductivity')),
            ("has_heat_production", _('Has heat gen')),
            ("no_data", _('No data')),
            ("no_sites", _('No sites or data')),
        )

    def queryset(self, request, qs):
        options = dict(
            has_heat_flow = qs.annotate(heat_flow=Coalesce('intervals__heat_flow_corrected', 'intervals__heat_flow_uncorrected')).exclude(heat_flow__isnull=True),
            has_gradient = qs.annotate(gradient=Coalesce('intervals__gradient_corrected', 'intervals__gradient_uncorrected')).exclude(gradient__isnull=True),
            has_temperature = qs.exclude(temperature__isnull=True),
            has_conductivity = qs.exclude(conductivity__isnull=True),
            has_heat_production = qs.exclude(heat_production__isnull=True),
            no_data=qs.filter(intervals__isnull=True, temperature__isnull=True,conductivity__isnull=True,heat_production__isnull=True),
            no_sites=qs.filter(intervals__isnull=True, temperature__isnull=True,conductivity__isnull=True,heat_production__isnull=True,sites__isnull=True),
        )
        return options.get(self.value())



class IsCorrectedFilter(admin.SimpleListFilter):

    title = _('corrected?')
    parameter_name = 'has_correction'

    def lookups(self, request, model_admin):

        return (
            ('yes', _('Yes')),
            ('no',  _('No')),
        )

    def queryset(self, request, queryset):

        if self.value() == 'yes':
            return queryset.exclude(gradient_corrected__isnull=True)

        if self.value() == 'no':
            return queryset.filter(gradient_corrected__isnull=True)