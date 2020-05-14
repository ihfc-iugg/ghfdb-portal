from import_export.admin import ImportExportActionModelAdmin
from django.shortcuts import resolve_url
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.utils.html import format_html
from django.db.models import Count
from django.contrib import admin
from django.db.models import F
from django.db import models
from django.utils.translation import gettext as _
from django.contrib.gis import admin as gisadmin



class BaseAdmin(gisadmin.ModelAdmin):
    exclude = ['edited_by','added_by','date_added','date_edited']
    # list_display

    def save_model(self, request, obj, form, change):
        if change:
            obj.edited_by = request.user._wrapped #add the current user to edited_by
        super().save_model(request, obj, form, change)

    def site_name(self,obj):
        return obj._site_name
    site_name.admin_order_field = '_site_name'

    def latitude(self,obj):
        return obj._latitude
    latitude.admin_order_field = '_latitude'

    def longitude(self,obj):
        return obj._longitude
    longitude.admin_order_field = '_longitude'
   
    def site_operator(self,obj):
        return obj._operator
    site_operator.admin_order_field = '_operator'

    def reference(self,obj):
        return obj._reference
    reference.admin_order_field = '_reference'

    def conductivity_count(self,obj):
        return obj._conductivity_count
    conductivity_count.admin_order_field = '_conductivity_count'

    def gradient_count(self,obj):
        return obj._gradient_count
    gradient_count.admin_order_field = '_gradient_count'

    def heat_gen_count(self,obj):
        return obj._heat_gen_count
    heat_gen_count.admin_order_field = '_heat_gen_count'

    def temperature_count(self,obj):
        return obj._temperature_count
    temperature_count.admin_order_field = '_temperature_count'

    def heat_flow_count(self,obj):
        return obj._heat_flow_count
    heat_flow_count.admin_order_field = '_heat_flow_count'

    def _conductivity(self,obj):
        return obj._conductivity
    _conductivity.admin_order_field = '_conductivity'

    def _heat_generation(self,obj):
        return obj._heat_generation
    _heat_generation.admin_order_field = '_heat_generation'
    
    def sites(self,obj):
        return obj._site_count
    sites.admin_order_field = '_site_count'

    def edit(self,obj):
        return _("edit")
    
class SitePropertyAdminMixin(BaseAdmin):
    list_display = ['edit','site_name','latitude','longitude','depth','sample_name','value','uncertainty','method','reference','age','age_min','age_max']
    # search_fields = ['depthinterval__reference__primary_author__last_name']
    fieldsets = [('Site', {'fields':[
                            'site']}),
                ('Sample', {'fields': [
                            'sample_name',
                            ('value','uncertainty'),
                            'method',
                            'depth',
                            ]}),
                ('Age', {'fields': [
                            ('age_min','age_max','age_method',),
                            ]}),
                ('Geology', {'fields': [
                            ('rock_type','rock_group','rock_origin')]}),
                            ]
    autocomplete_fields = ['site']
    list_filter = ['method']
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('site').annotate(
            _site_name=F('site__site_name'),
            _latitude=F('site__latitude'),
            _longitude=F('site__longitude'),)

        return queryset

class DepthIntervalMixin(BaseAdmin):
    autocomplete_fields = ['site']
    list_display = ['site_name','latitude','longitude','depth_min','depth_max','corrected','corrected_uncertainty','uncorrected','uncorrected_uncertainty','reference']
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('site').annotate(
            _site_name=F('site__site_name'),
            _latitude=F('site__latitude'),
            _longitude=F('site__longitude'),
            )
        return queryset
    
