from import_export.admin import ImportExportActionModelAdmin
from django.shortcuts import resolve_url
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.utils.html import format_html
from django.db.models import Count
from django.contrib import admin
from django.db.models import F

class BaseAdmin(admin.ModelAdmin):
    exclude = ['edited_by','added_by','date_added','data_edited']

    def save_model(self, request, obj, form, change):
        if change:
            obj.edited_by = request.user._wrapped #add the current user to edited_by
        super().save_model(request, obj, form, change)

class DataCountsMixin(BaseAdmin):
    pass
    # end_list_display = ['operator',  'date_created', 'last_modified', 'edited_by']
    
    # def conductivity(self,obj):
    #     return obj._conductivity_count
    # conductivity.admin_order_field = '_conductivity_count'

    # def heat_gen(self,obj):
    #     return obj._heat_gen_count
    # heat_gen.admin_order_field = '_heat_gen_count'

    # def temp(self,obj):
    #     return obj._temperature_count
    # temp.admin_order_field = '_temperature_count'

    # def heat_flow(self,obj):
    #     return obj._heat_flow_count
    # heat_flow.admin_order_field = '_heat_flow_count'

    # def sites(self,obj):
    #     return obj._site_count
    # sites.admin_order_field = '_site_count'

class SitePropertyAdminMixin(admin.ModelAdmin):

    list_display = ['site_name','latitude','longitude','depth','sample_name','value','uncertainty','method','number_of_measurements','reference','date_added','added_by','date_edited','edited_by']
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
                            ('rock_type','rock_group','rock_origin','lithology')]}),
                            ]

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
        queryset = queryset.select_related('site').annotate(
            _site_name=F('site__site_name'),
            _latitude=F('site__latitude'),
            _longitude=F('site__longitude'),)
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

    # def reference(self,obj):
    #     return obj._reference
    # reference.admin_order_field = '_reference'


    # def _reference(self,obj):
    #     return obj.reference
