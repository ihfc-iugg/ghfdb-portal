from django.contrib import admin
from .models import Site, Interval, Conductivity, HeatProduction, Temperature
from .mixins import BaseAdmin
from import_export.admin import ImportExportActionModelAdmin
from .mixins import SitePropertyAdminMixin
from .resources import ConductivityResource, HeatGenResource, IntervalResource, TempResource, SiteResource
from .models import Interval, Conductivity, HeatProduction
from django.db.models import F
from .filters import IsCorrectedFilter,IntervalType, EmptySites
from django.http import HttpResponse
from mapping import update
from django.utils.translation import gettext as _
import csv

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
    point_zoom = 3
    map_width = 900
    modifiable=False

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # queryset = queryset.prefetch_related('reference').select_related('country','continent')
        queryset = queryset.prefetch_related('reference')
        return queryset

    def _reference(self,obj):
        return ','.join([r.bib_id for r in obj.reference.all()])

    def recalculate_geo_fields(self, request, qs):
        geos = ['countries','continents','seas','basins','political','province']
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

@admin.register(Interval)
class IntervalAdmin(BaseAdmin,ImportExportActionModelAdmin):
    resource_class = IntervalResource
    autocomplete_fields = ['site']
    # search_fields = ['site__site_name','site__latitude','site__longitude','reference__bibtex','reference__id']
    search_fields = ['site__site_name']
    list_display = ['site_name','reference','depth_min','depth_max','reliability','heat_flow_corrected','heat_flow_uncorrected','gradient_corrected','gradient_uncorrected','average_conductivity','heat_production']

    list_filter = ['reliability',IsCorrectedFilter, IntervalType]
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
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('reference').select_related('site').annotate(
            _site_name=F('site__site_name'),
            _latitude=F('site__latitude'),
            _longitude=F('site__longitude'),
            )
        return queryset

    def mark_verified(self, request, queryset):
        queryset.update(is_immortal=True)

    def interval(self, obj):
        return '{}-{}'.format(obj.depth_min, obj.depth_max)

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
class HeatGenAdmin(SitePropertyAdminMixin,ImportExportActionModelAdmin):
    resource_class = HeatGenResource
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

# @admin.register(Publication)
# class PublicationAdmin(BaseAdmin):

#     list_display = ['edit','article','bib_id','is_verified','year', 'title', 'journal']
#     exclude = ['source',]
#     search_fields = ('pk', 'year', 'bib_id', 'bibtex')
#     fields = ['is_verified', ('bib_id','pk', 'slug'), 'file','bibtex',]
#     readonly_fields = ['pk','slug','bib_id']
#     list_filter = [EmptyPublications, VerifiedFilter, PubStatusFilter]
#     actions = ["export_bibtex","merge"]

#     def article(self,obj):
#         if obj.doi:
#             return mark_safe('<a href="https://doi.org/{}"><i class="fas fa-globe fa-lg"></i></a>'.format(obj.doi))
#         else:
#             return ''

#     def edit(self,obj):
#         return mark_safe('<i class="fas fa-edit"></i>')

#     def export_bibtex(self, request, qs):
#         """
#         Exports the selected rows using file_format.
#         """
#         bibtex_list = list(qs.values_list('bibtex',flat=True))
#         response = HttpResponse(''.join(bibtex_list), content_type='application/text charset=utf-8')
#         response['Content-Disposition'] = 'attachment; filename="ThermoGlobe.bib"'
#         return response
#     export_bibtex.short_description = _('Export bibtex')

#     def response_change(self, request, obj):
#         if "_upload" in request.POST:
#             # print('Doing something now')
#             # self.import_data(request,obj)
#             # obj.save()
#             # self.message_user(request, "The uploaded file was succesfully imported.")
#             return HttpResponseRedirect(".")
#         return super().response_change(request, obj)

#     def get_queryset(self, request):
#         return super().get_queryset(request).annotate(
#             _site_count=Count("sites",distinct=True),
#             )

#     def save_model(self, request, obj, form, change):
#         if change:
#             if form.instance.is_verified != form.initial['is_verified']:
#                 if form.instance.is_verified == True:
#                     form.instance.verified_by = request.user._wrapped
#                     form.instance.date_verified = timezone.now()
#         else:
#             form.instance.source = 'Admin Created'

#         super().save_model(request, obj, form, change)
#         bib = obj.get_bibtex_entry(form.instance.bibtex)
#         form.instance.bib_entry = bib


