from .models import Site, Conductivity, Interval, Author
from mapping.models import Sea, Country, Continent, Province
import django_filters
from django_filters import widgets, MultipleChoiceFilter, ChoiceFilter, ModelMultipleChoiceFilter,ModelChoiceFilter, RangeFilter
from django import forms
from thermoglobe.widgets import RangeField, RangeWidget
from django.contrib import admin
from django.utils.translation import gettext as _
from django.db.models import Q, Count
from django.db.models.functions import Length
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
                ('heat_generation','Heat Generation'),],
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
            choices=list(Continent.objects.exclude(sites__isnull=True).values_list('id','name').order_by('name')),
            lookup_expr='exact',
        )

    # country = ModelMultipleChoiceFilter(
    country = MultipleChoiceFilter(
            choices=list(Country.objects.exclude(sites__isnull=True).values_list('id','name').order_by('name')),
            lookup_expr='exact',
        )

    sea = MultipleChoiceFilter(
            lookup_expr='exact',
            choices = list(Sea.objects.exclude(sites__isnull=True).values_list('id','name').order_by('name')),
        )

    # sea = ModelMultipleChoiceFilter(
    #         queryset=Sea.objects.exclude(sites__isnull=True).values('id','name').order_by('name'),
    #         lookup_expr='exact',
    #     )

    province = MultipleChoiceFilter(
            choices=list(Province.objects.exclude(sites__isnull=True).values_list('id','name').order_by('name')),
            lookup_expr='exact',
        )

    tectonic_environment = MultipleChoiceFilter(
            choices = list(Province.objects.exclude(sites__isnull=True).values_list('type','type').distinct()),
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

class PublicationFilter(forms.Form):
    
    reference__first_author__last_name__iexact = forms.CharField(label='Author', max_length=50, strip=True, required=False, help_text='Search by last name of author')
    reference__year = RangeField(
                label='Year',
                required=False,
                help_text='Year of publication',
                field=forms.IntegerField())

    class Meta:
        title = 'reference'

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

class PubStatusFilter(admin.SimpleListFilter):
    """Show or hide if a publication has a complete reference or not
    """
    title = _('completion status')

    parameter_name = 'completion_status'

    def lookups(self, request, model_admin):
        return (
            ('done', _('Done')),
            ('has_id',  _('Has ID, no bibtex')),
            ('has_bibtex',  _('Has bibtex, bad ID')),
            ('no_id',  _('No ID, no bibtex')),
        )

    def queryset(self, request, qs):

        if self.value() == 'done':
            return qs.exclude(Q(bibtex='') & Q(title=''))

        if self.value() == 'has_id':
            return qs.annotate(bib_length=Length('bib_id')).exclude(Q(bib_length__lte=4)).filter(Q(bibtex=''))

        if self.value() == 'has_bibtex':
            return qs.annotate(bib_length=Length('bib_id')).filter(Q(bib_length__lte=4)).exclude(Q(bibtex=''))

        if self.value() == 'no_id':
            return qs.annotate(bib_length=Length('bib_id')).filter(Q(bib_length__lte=4) & Q(bibtex=''))


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
                heat_generation__isnull=True,
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
            ("has_heat_generation", _('Has heat gen')),
            ("no_data", _('No data')),
            ("no_sites", _('No sites or data')),
        )

    def queryset(self, request, qs):
        options = dict(
            has_heat_flow = qs.annotate(heat_flow=Coalesce('intervals__heat_flow_corrected', 'intervals__heat_flow_uncorrected')).exclude(heat_flow__isnull=True),
            has_gradient = qs.annotate(gradient=Coalesce('intervals__gradient_corrected', 'intervals__gradient_uncorrected')).exclude(gradient__isnull=True),
            has_temperature = qs.exclude(temperature__isnull=True),
            has_conductivity = qs.exclude(conductivity__isnull=True),
            has_heat_generation = qs.exclude(heat_generation__isnull=True),
            no_data=qs.filter(intervals__isnull=True, temperature__isnull=True,conductivity__isnull=True,heat_generation__isnull=True),
            no_sites=qs.filter(intervals__isnull=True, temperature__isnull=True,conductivity__isnull=True,heat_generation__isnull=True,sites__isnull=True),
        )
        return options.get(self.value())


class LastNameLengthFilter(admin.SimpleListFilter):
    """Show or hide if a publication has a complete reference or not
    """
    title = _('last_name_length')

    parameter_name = 'last_name_length'

    def lookups(self, request, model_admin):
        return (
            ('<2', _('< 2')),
        )

    def queryset(self, request, qs):

        if self.value() == '<2':
            return qs.annotate(last_name_length=Length('last_name')).filter(last_name_length__lte=2)

class DuplicateFilter(admin.SimpleListFilter):
    """Show or hide if a publication has a complete reference or not
    """
    title = _('Duplicates?')

    parameter_name = 'duplicates'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Maybe')),
        )

    def queryset(self, request, qs):
        
        if self.value() == 'yes':
            dups = (
                    Author.objects.values('last_name')
                    .annotate(count=Count('id'))
                    .values('last_name')
                    .order_by()
                    .filter(count__gt=1)
                )
            out = Author.objects.filter(last_name__in=dups)
            return out

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