from django.contrib import admin
from .models import Site, HeatFlow, Conductivity, HeatGeneration, Temperature, ThermalGradient, Correction
from .mixins import BaseAdmin
# from database.admin_inlines import CorrectionsInline, TemperatureInline, HeatFlowInline, HeatGenerationInline, ConductivityInline
from import_export.admin import ImportExportActionModelAdmin, ImportForm
from .mixins import SitePropertyAdminMixin, DepthIntervalMixin
from .resources import ConductivityResource, HeatGenResource, HeatFlowResource, TempResource
from .models import HeatFlow, ThermalGradient, Conductivity, HeatGeneration
from django.db.models import F, Count
from .filters import IsCorrectedFilter
from main import inlines

@admin.register(Site)
class SiteAdmin(BaseAdmin, ImportExportActionModelAdmin):
    resource_class = HeatFlowResource
    list_display = ['site_name', 'latitude', 'longitude','elevation', 'heat_flow_count','conductivity_count','heat_gen_count','temperature_count', 'operator','edited_by','date_edited']

    readonly_fields = ["seamount_distance", "outcrop_distance", "ruggedness",'sediment_thickness','crustal_thickness']

    # inlines = [inlines.HeatFlow,inlines.SedimentThickness]

    fieldsets = [
        ("Site Information", 
            {'fields': [
                'site_name',
                'geom',
                ('latitude','longitude','elevation'),
                ('operator','cruise'),
                'country',
                'sea',]}),
        ('Calculated Fields',
            {'fields': [ 
                'seamount_distance',
                'outcrop_distance',
                'ruggedness',
                'sediment_thickness',
                'crustal_thickness']}),
        ('Reported Fields',
            {'fields': [
                ('surface_temp','bottom_hole_temp'),
                ('well_depth','dip',),
                ]}),        
        ('Geology',
            {'fields': [ 
                ('basin','sub_basin'),
                'tectonic_environment',
                # 'geo_province',
                'lithology']}),
        ('Reference',
            {'fields': [ 
                'reference',]}),                
                ]

    # inlines = [HeatFlowInline, TemperatureInline, HeatGenerationInline, ]
    search_fields = ['site_name','latitude','longitude','reference__bib_id']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _heat_flow_count=Count('heatflow'),
            _conductivity_count=Count('conductivity'),
            _heat_gen_count=Count('heatgeneration'),
            _temperature_count=Count('temperature'),)
        return queryset

@admin.register(ThermalGradient)
class GradientAdmin(DepthIntervalMixin):
    fieldsets = [
        ('Temperature Gradient',
            {'fields': [
                ('corrected','corrected_uncertainty'),
                ('uncorrected','uncorrected_uncertainty'),]})]

    inlines = [inlines.Corrections,]

@admin.register(HeatFlow)
class HeatFlowAdmin(DepthIntervalMixin,ImportExportActionModelAdmin):
    resource_class = HeatFlowResource

    search_fields = ['site__site_name','reference__bib_id']

    list_display = ['site_name','latitude','longitude','reference','depth_min','depth_max','reliability','corrected','corrected_uncertainty','uncorrected','uncorrected_uncertainty','conductivity','conductivity_uncertainty']

    inlines = [inlines.Corrections]

    list_filter = ['reliability',IsCorrectedFilter,'site__site_type']
    fieldsets = [
        ('Heat Flow',
            {'fields': [
                ('depth_min', 'depth_max'),
                'reliability',
                ('corrected','corrected_uncertainty'),
                ('uncorrected','uncorrected_uncertainty'),
                ]
            }
        ),
        ('Thermal Conductivity',
            {'fields': [
                ('conductivity', 'conductivity_uncertainty','number_of_conductivities'),
                'conductivity_method',
                ],
            'classes': ('collapse',),
            }
        ),
        ('Reference',
            {'fields': ['reference',
                ]
            }
        ),                  
                
                ]
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset

@admin.register(Conductivity)
class ConductivityAdmin(SitePropertyAdminMixin,ImportExportActionModelAdmin):
    resource_class = ConductivityResource
    search_fields = ['site__site_name','site__latitude','site__longitude','reference__bib_id']

@admin.register(HeatGeneration)
class HeatGenAdmin(SitePropertyAdminMixin,ImportExportActionModelAdmin):
    resource_class = HeatGenResource
    search_fields = ['site__site_name','site__latitude','site__longitude','reference__bib_id']


@admin.register(Temperature)
class TemperatureAdmin(BaseAdmin,ImportExportActionModelAdmin):
    resource_class=TempResource
    list_display = ['edit','site_name','latitude','longitude','depth','value','method','site_operator','reference']
    list_filter = ['is_bottom_of_hole','method']
    autocomplete_fields = ['site']
    search_fields = ['site__site_name','reference__bib_id','site__operator__name']
    fieldsets = [('Site', {'fields':['site']}),
                ('Measurement', {'fields': [
                        'value',
                        'depth',
                        'method',
                        'lag_time',
                        'is_bottom_of_hole',
                            ]}),
                ('Reference',{'fields':['reference']})
                            ]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('site').annotate(
            _site_name=F('site__site_name'),
            _latitude=F('site__latitude'),
            _longitude=F('site__longitude'),
            _operator=F('site__operator__name'),
            )

        return queryset

