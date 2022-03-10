from django.contrib import admin
from .models import TemperatureLog, ConductivityLog, HeatProductionLog
from .models import Conductivity, HeatProduction, Temperature
from thermoglobe.mixins import BaseAdmin
from import_export.admin import ImportExportActionModelAdmin
from .resources import ConductivityResource, HeatProductionResource, TempResource
from django.db.models import F, Count, Min, Max
from django.utils.translation import gettext as _


class AbstractAdmin(BaseAdmin, ImportExportActionModelAdmin):

    list_filter = ['source','method']
    autocomplete_fields = ['site']
    search_fields = ['site__site_name','site__latitude','site__longitude','id']
    readonly_fields = ['added']
    fieldsets = [
            ('Site', {'fields':['site',]}),
            ('Log Information', {'fields': [
                'year_logged',
                'method',
                'comment',
                'formation',
            ]}),
            ('Data Source', 
                {'fields':[
                    'reference',
                    ('source', 'source_id'),
                    'operator',
                ]}),
            ('Additional Information', 
                {'fields':[
                    'added',
                ]})
    ]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('site').prefetch_related('data').annotate(
            _site_name=F('site__site_name'),
            _latitude=F('site__latitude'),
            _longitude=F('site__longitude'),
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

# Register your models here.
@admin.register(TemperatureLog)
class TemperatureLogAdmin(AbstractAdmin):
    resource_class=TempResource
    list_display = [
        'edit','site_name','latitude','longitude', 
        'min_depth', 'max_depth', 'data_count', 'year_logged', 
        'method', 'correction', 'circ_time','lag_time',
        'reference','operator', 'source']

    fieldsets = [
            ('Site', {'fields':['site',]}),
            ('Log Information', {'fields': [
                'year_logged',
                ('circ_time','lag_time'),
                'method', 
                'correction',
                'comment',
                'formation',
                ]}),
            ('Data Source', 
                {'fields':[
                    'reference',
                    ('source', 'source_id'),
                    'operator',
                ]}),
            ('Additional Information', 
                {'fields':[
                    'added',
                ]})
        ]


@admin.register(ConductivityLog)
class ConductivityAdmin(AbstractAdmin):
    resource_class = ConductivityResource
    list_display = [
        'edit','site_name','latitude','longitude', 
        'min_depth','max_depth', 'data_count', 'year_logged', 
        'method', 'reference','operator', 'source']

@admin.register(HeatProductionLog)
class HeatProductionAdmin(AbstractAdmin):
    resource_class = HeatProductionResource
    list_display = [
        'edit','site_name','latitude','longitude', 
        'min_depth','max_depth', 'data_count', 'year_logged', 
        'method', 'reference','operator', 'source']


# admin.site.register(Conductivity, ImportExportActionModelAdmin)
# admin.site.register(Temperature, ImportExportActionModelAdmin)
# admin.site.register(HeatProduction, ImportExportActionModelAdmin)