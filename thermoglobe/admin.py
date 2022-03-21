from django.contrib import admin
from .models import Site
from .models.interval import HeatFlow, Gradient, Correction
from .mixins import BaseAdmin
from import_export.admin import ImportExportActionModelAdmin
from .resources import IntervalResource, SiteResource
from django.db.models import F
from .filters import IsCorrectedFilter, EmptySites
from django.http import HttpResponse
from django.utils.translation import gettext as _
import csv
from django.db.models.functions import Coalesce

@admin.register(Site)
class SiteAdmin(BaseAdmin, ImportExportActionModelAdmin):
    change_list_template = 'smuggler/change_list.html'
    resource_class = SiteResource
    list_display = ['site_name', 'latitude', 'longitude','elevation','well_depth','cruise','seafloor_age','_reference']
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
        return ','.join([r.label for r in obj.reference.all() if r.label])

    def recalculate_geo_fields(self, request, qs):
        geos = ['countries','continents','seas','political','province']
        # for geo in geos:
        #     getattr(update,geo)()

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
    list_display = ['site_name','depth_min','depth_max','reliability','_corrected','heat_flow','cond_ave','heat_prod','reference']
    # list_display = ['site_name','depth_min','depth_max','reliability','_corrected','cond_ave','heat_production','reference']

    list_filter = ['reliability',IsCorrectedFilter]
    fieldsets = [ 
        ('Site',{'fields':['site']}),
        ('Interval', 
            {'fields': [
                'reference',
                ('depth_min', 'depth_max'),
                ('num_temp','temp_method'),
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
                ('cond_ave', 'cond_unc','num_cond'),
                'cond_method',
                ],
            # 'classes': ('collapse',),
            }
        ),
        ('heat production',
            {'fields': [
                ('heat_prod', 'heat_prod_unc','num_heat_prod'),
                'heat_prod_method',
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
        return (super().get_queryset(request).heat_flow()
                .prefetch_related('reference')
                .select_related('site')
                .annotate(
                    _site_name=F('site__site_name'),
                    _latitude=F('site__latitude'),
                    _longitude=F('site__longitude'),
                    ))

    def heat_flow(self, obj):
        return obj.heat_flow

    def mark_verified(self, request, queryset):
        queryset.update(is_verified=True)

@admin.register(Gradient)
class GradientAdmin(BaseAdmin,ImportExportActionModelAdmin):
    resource_class = IntervalResource
    autocomplete_fields = ['site']
    search_fields = ['site__site_name']
    list_display = ['site_name','depth_min','depth_max','_corrected','gradient','reference']
    # list_display = ['site_name','depth_min','depth_max','_corrected','reference']

    list_filter = [IsCorrectedFilter]
    fieldsets = [ 
        ('Site',{'fields':['site']}),
        ('Interval', 
            {'fields': [
                'reference',
                ('depth_min', 'depth_max'),
                ('num_temp','temp_method'),
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
                ('cond_ave', 'cond_unc','num_cond'),
                'cond_method',
                ],
            # 'classes': ('collapse',),
            }
        ),
        ('heat production',
            {'fields': [
                ('heat_production', 'heat_prod_unc ','num_heat_prod'),
                'heat_prod_method',
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
        return (super().get_queryset(request).gradient()
                .prefetch_related('reference')
                .select_related('site')
                .annotate(
                    _site_name=F('site__site_name'),
                    ))

    def gradient(self, obj):
        return obj.gradient

    def mark_verified(self, request, queryset):
        queryset.update(is_verified=True)

