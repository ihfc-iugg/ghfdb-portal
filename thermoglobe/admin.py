from django.contrib import admin
from .models import Site, Interval, Conductivity, HeatProduction, Temperature
from .models.interval import HeatFlow, Gradient
from .mixins import BaseAdmin
from import_export.admin import ImportExportActionModelAdmin
from .mixins import SitePropertyAdminMixin
from .resources import ConductivityResource, HeatProductionResource, IntervalResource, TempResource, SiteResource
from .models import Interval, Conductivity, HeatProduction
from django.db.models import F
from .filters import IsCorrectedFilter,IntervalType, EmptySites
from django.http import HttpResponse
from mapping import update
from django.utils.translation import gettext as _
import csv
from django.db.models.functions import Coalesce

@admin.register(Site)
class SiteAdmin(BaseAdmin, ImportExportActionModelAdmin):
    resource_class = SiteResource
    list_display = ['site_name', 'latitude', 'longitude','elevation','_reference']
    readonly_fields = ['id','slug',"seamount_distance", "outcrop_distance", 'sediment_thickness','crustal_thickness']
    actions = ['export_sites',"merge",'recalculate_geo_fields']
    list_filter = [EmptySites,]

    filter_horizontal = ['reference']
    fieldsets = [
        ("Site Information", 
            {'fields': [
                ('id','slug'),
                'geom',
                'site_name',
                ('latitude','longitude','elevation'),
                ('cruise'),
                ('well_depth',),
                ]}), 
        ('Calculated Fields',
            {'fields': [ 
                ('seamount_distance',
                'outcrop_distance',
                'sediment_thickness',
                'crustal_thickness')]}),
        ('Publication',
            {'fields': [ 
                'reference',]}),                
                ]

    search_fields = ['id','site_name','latitude','longitude','reference__bibtex','reference__id']
    point_zoom = 8
    map_width = 900
    # modifiable=False

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # queryset = queryset.prefetch_related('reference').select_related('country','continent')
        queryset = queryset.prefetch_related('reference')
        return queryset

    def _reference(self,obj):
        return ','.join([r.citekey for r in obj.reference.all() if r.citekey])

    def recalculate_geo_fields(self, request, qs):
        geos = ['countries','continents','seas','political','province']
        for geo in geos:
            getattr(update,geo)()

    def export_sites(self, request, qs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sites.csv"'

        writer = csv.writer(response)
        vals = ['id', 'latitude','longitude']
        writer.writerow(vals)
        data = qs.values_list(*vals)
        for row in data:
            writer.writerow(row)

        return response

@admin.register(HeatFlow)
class HeatFlowAdmin(BaseAdmin,ImportExportActionModelAdmin):
    resource_class = IntervalResource
    autocomplete_fields = ['site']
    search_fields = ['site__site_name']
    list_display = ['site_name','depth_min','depth_max','reliability','_corrected','heat_flow','average_conductivity','heat_production','reference']

    list_filter = ['reliability',IsCorrectedFilter]
    fieldsets = [ 
        ('Site',{'fields':['site']}),
        ('Interval', 
            {'fields': [
                'reference',
                ('depth_min', 'depth_max'),
                ('number_of_temperatures','temp_method'),
                ('global_flag','global_reason','global_by'),
                'comment',
                ]
            }
        ),
        ('Heat Flow',
            {'fields': [
                'reliability',
                ('heat_flow_corrected','heat_flow_corrected_uncertainty'),
                ('heat_flow_uncorrected','heat_flow_uncorrected_uncertainty'),
                ]
            }
        ),
        ('Temperature Gradient',
            {'fields': [
                ('gradient_corrected','gradient_corrected_uncertainty'),
                ('gradient_uncorrected','gradient_uncorrected_uncertainty'),
                ]
            }
        ),
        ('Thermal Conductivity',
            {'fields': [
                ('average_conductivity', 'conductivity_uncertainty','number_of_conductivities'),
                'conductivity_method',
                ],
            # 'classes': ('collapse',),
            }
        ),
        ('heat production',
            {'fields': [
                ('heat_production', 'heat_production_uncertainty','number_of_heat_gen'),
                'heat_production_method',
                ],
            # 'classes': ('collapse',),
            }
        ),                
    ]
    actions = ["mark_verified"] + ImportExportActionModelAdmin.actions


    def save_model(self, request, obj, form, change):
        if change:
            if form.instance.global_flag != form.initial['global_flag']:
                if form.instance.global_flag == True:
                    form.instance.global_by = request.user._wrapped
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        return (super().get_queryset(request)
                .annotate(heat_flow=Coalesce('heat_flow_corrected', 'heat_flow_uncorrected'))
                .exclude(heat_flow__isnull=True)
                .prefetch_related('reference')
                .select_related('site')
                .annotate(
                    _site_name=F('site__site_name'),
                    _latitude=F('site__latitude'),
                    _longitude=F('site__longitude'),
                    ))

    def mark_verified(self, request, queryset):
        queryset.update(is_verified=True)

@admin.register(Gradient)
class GradientAdmin(BaseAdmin,ImportExportActionModelAdmin):
    resource_class = IntervalResource
    autocomplete_fields = ['site']
    search_fields = ['site__site_name']
    list_display = ['site_name','depth_min','depth_max','_corrected','gradient','reference']

    list_filter = [IsCorrectedFilter]
    fieldsets = [ 
        ('Site',{'fields':['site']}),
        ('Interval', 
            {'fields': [
                'reference',
                ('depth_min', 'depth_max'),
                ('number_of_temperatures','temp_method'),
                ('global_flag','global_reason','global_by'),
                'comment',
                ]
            }
        ),
        ('Heat Flow',
            {'fields': [
                'reliability',
                ('heat_flow_corrected','heat_flow_corrected_uncertainty'),
                ('heat_flow_uncorrected','heat_flow_uncorrected_uncertainty'),
                ]
            }
        ),
        ('Temperature Gradient',
            {'fields': [
                ('gradient_corrected','gradient_corrected_uncertainty'),
                ('gradient_uncorrected','gradient_uncorrected_uncertainty'),
                ]
            }
        ),
        ('Thermal Conductivity',
            {'fields': [
                ('average_conductivity', 'conductivity_uncertainty','number_of_conductivities'),
                'conductivity_method',
                ],
            # 'classes': ('collapse',),
            }
        ),
        ('heat production',
            {'fields': [
                ('heat_production', 'heat_production_uncertainty','number_of_heat_gen'),
                'heat_production_method',
                ],
            # 'classes': ('collapse',),
            }
        ),                
    ]
    actions = ["mark_verified"] + ImportExportActionModelAdmin.actions


    def save_model(self, request, obj, form, change):
        if change:
            if form.instance.global_flag != form.initial['global_flag']:
                if form.instance.global_flag == True:
                    form.instance.global_by = request.user._wrapped
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        return (super().get_queryset(request)
                .annotate(gradient=Coalesce('gradient_corrected', 'gradient_uncorrected'))
                .exclude(gradient__isnull=True)
                .prefetch_related('reference')
                .select_related('site')
                .annotate(
                    _site_name=F('site__site_name'),
                    ))

    def mark_verified(self, request, queryset):
        queryset.update(is_verified=True)

@admin.register(Conductivity)
class ConductivityAdmin(SitePropertyAdminMixin,ImportExportActionModelAdmin):
    resource_class = ConductivityResource
    list_display = ['edit','site_name','latitude','longitude','depth','conductivity','uncertainty','method','reference']

    fieldsets = [('Site', {'fields':[
                            'site']}),
                ('Sample', {'fields': [
                            'sample_name',
                            'rock_type',
                            ('conductivity','uncertainty'),
                            'method',
                            'depth',
                            ]}),
                        ]

@admin.register(HeatProduction)
class HeatProductionAdmin(SitePropertyAdminMixin,ImportExportActionModelAdmin):
    resource_class = HeatProductionResource
    list_display = ['edit','site_name','latitude','longitude','depth','heat_production','uncertainty','method','reference']

    fieldsets = [('Site', {'fields':[
                            'site']}),
                ('Sample', {'fields': [
                            'sample_name',
                            'rock_type',
                            ('heat_production','uncertainty'),
                            'method',
                            'depth',
                            ]}),
            ]

@admin.register(Temperature)
class TemperatureAdmin(BaseAdmin,ImportExportActionModelAdmin):
    resource_class=TempResource
    list_display = ['edit','site_name','latitude','longitude','depth','temperature','method','circ_time','lag_time','reference']
    list_filter = ['source','method']
    autocomplete_fields = ['site']
    search_fields = ['site__site_name','site__latitude','site__longitude','reference__bib_id']
    fieldsets = [('Site', {'fields':['site']}),
                ('Measurement', {'fields': [
                        'temperature',
                        'depth',
                        'method',
                        'lag_time',
                        'comment',
                            ]}),
                ('Publication',{'fields':['reference']})
                            ]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('site').annotate(
            _site_name=F('site__site_name'),
            _latitude=F('site__latitude'),
            _longitude=F('site__longitude'),
            )

        return queryset
