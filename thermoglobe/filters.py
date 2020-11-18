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

    continent = ModelMultipleChoiceFilter(
            queryset=Continent.objects.exclude(sites__isnull=True).order_by('name'),
            lookup_expr='exact',
        )

    country = ModelMultipleChoiceFilter(
            queryset=Country.objects.exclude(sites__isnull=True).order_by('name'),
            lookup_expr='exact',
        )

    sea = ModelMultipleChoiceFilter(
            queryset=Sea.objects.exclude(sites__isnull=True).order_by('name'),
            lookup_expr='exact',
        )

    province = ModelMultipleChoiceFilter(
            queryset=Province.objects.exclude(sites__isnull=True).order_by('name'),
            lookup_expr='exact',
        )

    tectonic_environment = MultipleChoiceFilter(
            choices = list(Province.objects.exclude(sites__isnull=True).values_list('type','type').distinct()),
            field_name='province__type',
            lookup_expr='exact',
            label='Tectonic Environment'
        )

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

# class ActiveFilter(admin.SimpleListFilter):

#     title = _('is active')

#     parameter_name = 'is_active'

#     def lookups(self, request, model_admin):
#         return (
#             ('yes', _('Yes')),
#             ('no',  _('No')),
#         )

#     def queryset(self, request, queryset):
#         queryset = queryset.annotate(
#             is_active=Q(heatflow__isnull=True) & Q(conductivity__isnull=True)
        
#         )
#         queryset[0].is_active
#         if self.value() == 'yes':
#             return queryset.filter(is_active=False)

#         if self.value() == 'no':
#             return queryset.filter(is_active=True)


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