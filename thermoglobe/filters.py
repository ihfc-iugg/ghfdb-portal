from .models import Site
from mapping.models import Sea, Country, Continent, Province
import django_filters
from django_filters import MultipleChoiceFilter, ChoiceFilter, RangeFilter
from django.contrib import admin
from django.utils.translation import gettext as _
from django.db.models import Q
from django.db import models
from thermoglobe.forms import DownloadForm
from django.db.models.functions import Coalesce

class Filter(django_filters.FilterSet):

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

    longitude = RangeFilter()
    latitude = RangeFilter()
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

    sea = MultipleChoiceFilter(
            lookup_expr='exact',
            choices = Sea.objects.exclude(sites__isnull=True).values_list('id','name').order_by('name'),
        )

    # sea = ModelMultipleChoiceFilter(
    #         queryset=Sea.objects.exclude(sites__isnull=True).values('id','name').order_by('name'),
    #         lookup_expr='exact',
    #     )

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
    download_form = DownloadForm()

    class Meta:
        model = Site
        fields = ['latitude','longitude','elevation','country','continent','sea','province']
        # fields = ['value','latitude','longitude','elevation','country','continent','sea','province']

class VerifiedFilter(admin.SimpleListFilter):

    title = _('is verified')

    parameter_name = 'is_verified'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no',  _('No')),
        )

    def queryset(self, request, queryset):

        if self.value() == 'yes':
            return queryset.filter(is_verified=False)

        if self.value() == 'no':
            return queryset.filter(is_verified=True)

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

class IntervalType(admin.SimpleListFilter):
    """Show or hide if a publication has a complete reference or not
    """
    title = _('interval type')

    parameter_name = 'interval_type'

    def lookups(self, request, model_admin):
        return (
            ('hf', _('Heat flow')),
            ('tg', _('Gradient')),
        )

    def queryset(self, request, qs):
        
        if self.value() == 'hf':
            return qs.filter(Q(heat_flow_corrected__isnull=False) | Q(heat_flow_uncorrected__isnull=False))
        if self.value() == 'tg':
            return qs.filter(Q(gradient_corrected__isnull=False) | Q(gradient_uncorrected__isnull=False))

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