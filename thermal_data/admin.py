from django.contrib import admin
from .models import TemperatureLog, ConductivityLog
from geoluminate.admin_tools.mixins import BaseAdmin
from import_export.admin import ImportExportActionModelAdmin
from .resources import ConductivityResource, TempResource
from django.db.models import F, Count, Min, Max
from django.utils.translation import gettext as _
from well_logs.models import Log

admin.site.unregister(Log)


class AbstractAdmin(BaseAdmin, ImportExportActionModelAdmin):

    list_filter = ['source', 'method']
    autocomplete_fields = ['site']
    search_fields = ['site__name', 'site__lat', 'site__lng', 'id']
    readonly_fields = ['added', 'modified']
    fieldsets = [
        ('Site', {'fields': ['site', ]}),
        ('Log Information', {'fields': [
            'year_logged',
            'method',
            'comment',
        ]}),
        ('Data Source',
         {'fields': [
             'reference',
             ('source', 'source_id'),
             'operator',
         ]}),
        ('Additional Information',
         {'fields': [
             'added',
         ]})
    ]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('site').prefetch_related('data').annotate(
            _name=F('site__name'),
            _lat=F('site__lat'),
            _lng=F('site__lng'),
            _data_count=Count('data'),
            _min_depth=Min('data__depth'),
            _max_depth=Max('data__depth'),
        )
        return queryset

    def data_count(self, obj):
        return obj._data_count
    data_count.admin_order_field = '_data_count'
    data_count.short_description = _('count (n)')

    def min_depth(self, obj):
        return obj._min_depth
    min_depth.admin_order_field = '_min_depth'
    min_depth.short_description = _('upper depth (m)')

    def max_depth(self, obj):
        return obj._max_depth
    max_depth.admin_order_field = '_max_depth'
    max_depth.short_description = _('lower depth (m)')


@admin.register(TemperatureLog)
class TemperatureLogAdmin(AbstractAdmin):

    resource_class = TempResource

    list_display = [
        'id', 'name', 'latitude', 'longitude',
        'min_depth', 'max_depth', 'data_count', 'start_time', 'finish_time',
        'method', 'correction', 'circ_time', 'lag_time',
        'reference', 'operator', 'source']

    fieldsets = [
        ('Site', {'fields': ['site', ]}),
        ('Log Information', {'fields': [
            ('circ_time', 'lag_time'),
            'method',
            'correction',
            'comment',
        ]}),
        ('Data Source',
         {'fields': [
             'reference',
             ('source', 'source_id'),
             'operator',
         ]}),
        ('Additional Information',
         {'fields': [
             'added',
         ]})
    ]


@admin.register(ConductivityLog)
class ConductivityAdmin(AbstractAdmin):
    resource_class = ConductivityResource
    list_display = [
        'edit', 'name', 'latitude', 'longitude',
        'min_depth', 'max_depth', 'data_count', 'start_time', 'finish_time',
        'method', 'reference', 'operator', 'source']
