from import_export.admin import ImportExportActionModelAdmin
from django.shortcuts import resolve_url
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.utils.html import format_html
from django.db.models import Count
from django.contrib import admin
from django.db.models import F
from tinymce.widgets import TinyMCE
from django.db import models


class BaseAdmin(admin.ModelAdmin):
    exclude = ['edited_by','added_by','date_added','date_edited']
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
        }

    def save_model(self, request, obj, form, change):
        if change:
            obj.edited_by = request.user._wrapped #add the current user to edited_by
        super().save_model(request, obj, form, change)

class SitePropertyAdminMixin(BaseAdmin):

    list_display = ['site_name','latitude','longitude','_depth','sample_name','value','uncertainty','method','number_of_measurements','reference','date_added','added_by','date_edited','edited_by']
    search_fields = ['depthinterval__reference__primary_author__last_name']
    fieldsets = [('Site', {'fields':[
                            ('site','depth_interval')]}),
                ('Sample', {'fields': [
                            ('value','uncertainty'),
                            'depth',
                            'sample_name',
                            'method',
                            'number_of_measurements',]}),
                ('Age', {'fields': [
                            ('age_min','age_max','age_method',),
                            ]}),
                ('Geology', {'fields': [
                            ('lithology','rock_group','rock_origin')]}),
                            ]
    autocomplete_fields = ['site','depth_interval','lithology']

    def save_model(self, request, obj, form, change):
        user = request.user._wrapped
        
        if obj._state.adding is True:
            obj.added_by = user.username
            obj.edited_by = user 
        if change:
            obj.edited_by = request.user._wrapped 
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('site','depth_interval').annotate(
            _site_name=F('site__site_name'),
            _latitude=F('site__latitude'),
            _longitude=F('site__longitude'),
            _depth_min=F('depth_interval__depth_min'),
            _depth_max=F('depth_interval__depth_max'),
            
            )

        return queryset

    def site_name(self,obj):
        return obj._site_name
    site_name.admin_order_field = '_site_name'

    def latitude(self,obj):
        return obj._latitude
    latitude.admin_order_field = '_latitude'

    def longitude(self,obj):
        return obj._longitude
    longitude.admin_order_field = '_longitude'

    def _depth(self,obj):
        if obj.depth:
            return obj.depth
        elif obj._depth_min and obj._depth_max:
            return '{}-{}'.format(obj._depth_min,obj._depth_max)
        else:
            ''

    # def reference(self,obj):
    #     return obj._reference
    # reference.admin_order_field = '_reference'


    # def _reference(self,obj):
    #     return obj.reference

class DataCountsMixin(SitePropertyAdminMixin):
    autocomplete_fields = ['site','depth_interval']

    list_display = ['site_name','latitude','longitude','depth_min','depth_max','corrected','corrected_uncertainty','uncorrected','uncorrected_uncertainty','conductivity_count','heat_gen_count']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('site','depth_interval').annotate(
            _site_name=F('site__site_name'),
            _latitude=F('site__latitude'),
            _longitude=F('site__longitude'),
            _depth_min=F('depth_interval__depth_min'),
            _depth_max=F('depth_interval__depth_max'),
            )
        return queryset
    
    def depth_min(self,obj):
        return obj._depth_min
    depth_min.admin_order_field = '_depth_min'

    def depth_max(self,obj):
        return obj._depth_max
    depth_max.admin_order_field = '_depth_max'

    def conductivity_count(self,obj):
        return obj._conductivity
    conductivity_count.admin_order_field = '_conductivity'

    def heat_gen_count(self,obj):
        return obj._heat_generation
    heat_gen_count.admin_order_field = '_heat_generation'

    # def temp(self,obj):
    #     return obj._temperature_count
    # temp.admin_order_field = '_temperature_count'

    # def heat_flow(self,obj):
    #     return obj._heat_flow_count
    # heat_flow.admin_order_field = '_heat_flow_count'

    # def sites(self,obj):
    #     return obj._site_count
    # sites.admin_order_field = '_site_count'