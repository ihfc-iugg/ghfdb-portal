from django.contrib import admin
from .models import Site, HeatFlow, Conductivity, HeatGeneration, Temperature, Correction
from .mixins import BaseAdmin
from import_export.admin import ImportExportActionModelAdmin, ImportForm
from .mixins import SitePropertyAdminMixin, DepthIntervalMixin
from .resources import ConductivityResource, HeatGenResource, HeatFlowResource, TempResource
from .models import HeatFlow, Conductivity, HeatGeneration
from django.db.models import F, Count, Exists
from .filters import IsCorrectedFilter
from . import inlines


@admin.register(Site)
class SiteAdmin(BaseAdmin, ImportExportActionModelAdmin):
    resource_class = HeatFlowResource
    list_display = ['site_name', 'latitude', 'longitude','elevation','country','continent','CGG_basin', 'heat_flow_count','conductivity_count','heat_gen_count','temperature_count', 'operator',]

    readonly_fields = ["seamount_distance", "outcrop_distance", 'sediment_thickness','crustal_thickness']

    # inlines = [inlines.HeatFlow,inlines.SedimentThickness]
    filter_horizontal = ['reference']
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
                'sediment_thickness',
                'crustal_thickness']}),
        ('Reported Fields',
            {'fields': [
                ('surface_temp','bottom_hole_temp', 'bottom_water_temp'),
                ('well_depth',),
                ]}),        
        # ('Geology',
        #     {'fields': [ 
        #         'lithology']}),
        ('Publication',
            {'fields': [ 
                'reference',]}),                
                ]

    # inlines = [HeatFlowInline, TemperatureInline, HeatGenerationInline, ]
    search_fields = ['site_name','latitude','longitude','reference__bib_id']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _heat_flow_count=Count('heat_flow'),
            _gradient_count=Count('gradients'),
            _conductivity_count=Count('conductivity'),
            _heat_gen_count=Count('heatgeneration'),
            _temperature_count=Count('temperature'),)
        return queryset

# @admin.register(ThermalGradient)
# class GradientAdmin(DepthIntervalMixin):
#     fieldsets = [
#         ('Temperature Gradient',
#             {'fields': [
#                 ('corrected','corrected_uncertainty'),
#                 ('uncorrected','uncorrected_uncertainty'),]})]

#     inlines = [inlines.Corrections,]

@admin.register(HeatFlow)
class HeatFlowAdmin(DepthIntervalMixin,ImportExportActionModelAdmin):
    resource_class = HeatFlowResource
    search_fields = ['site__site_name','reference__bib_id']
    list_display = ['site_name','reference','depth_min','depth_max','reliability','heat_flow_corrected','heat_flow_corrected_unc','heat_flow_uncorrected','heat_flow_uncorrected_unc','conductivity','conductivity_uncertainty']
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
        ('Publication',
            {'fields': ['reference',
                ]
            }
        ),                  
                
                ]
    actions = ["mark_verified"] + ImportExportActionModelAdmin.actions

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset

    # def has_corrections(self,obj):
    #     try:
    #         if obj.corrections:
    #             return True
    #     except Exception:
    #         return False
    # has_corrections.boolean = True

        # return obj.corrected.isnull()

    def mark_verified(self, request, queryset):
        queryset.update(is_immortal=True)

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
                ('Publication',{'fields':['reference']})
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

