from reference.models import Reference
import django_filters
from django_filters import widgets

class ReferenceFilter(django_filters.FilterSet):

    last_name = django_filters.CharFilter(
        field_name='first_author__last_name',
        lookup_expr='icontains',
        label='Last name',)

    year_min = django_filters.NumberFilter(
        field_name='year',
        lookup_expr='gte',
        label='Year min',)

    year_max = django_filters.NumberFilter(
        field_name='year',
        lookup_expr='lte',
        label='Year max',)

    class Meta:
        model = Reference
        fields = ['last_name']
        # fields = {
        #     'primary_author__last_name': ['istartswith'],
        #     'year': ['gt','lt'],
        # }
