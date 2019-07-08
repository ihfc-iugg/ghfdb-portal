from import_export.admin import ImportExportActionModelAdmin
from django.shortcuts import resolve_url
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.utils.html import format_html
from django.db.models import Count
from django.contrib import admin

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


