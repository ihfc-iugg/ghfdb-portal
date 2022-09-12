from django.contrib.gis import admin
from .models import Country, Continent, Ocean, Political, Ocean
from django.db.models import Count, Avg
from django.db.models.functions import Coalesce
from django.urls import path
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.utils.encoding import force_str
from import_export.admin import ImportMixin
from django.utils.translation import gettext_lazy as _
from .forms import ConfirmImportForm, ImportForm
import zipfile as zf
from django.contrib.gis.utils import LayerMapping
from django.core.cache import caches
from import_export.admin import ImportExportActionModelAdmin

class SiteCountMixin:

    def get_queryset(self, request):
        return (super().get_queryset(request)
        .annotate(
            _site_count=Count("sites"),
            )
        )

    def site_count(self,obj):
        return obj._site_count
    site_count.admin_order_field = '_site_count'
    site_count.short_description = _('Site count')

class MappingAbstract(SiteCountMixin, admin.GeoModelAdmin):

    def ave_heat_flow(self,obj):
        return obj._ave_heat_flow
    ave_heat_flow.admin_order_field = '_ave_heat_flow'



@admin.register(Country)
class CountryAdmin(MappingAbstract):
    list_display = ['name','iso3','region','subregion','site_count']
    search_fields = ['name','region','subregion',]
    list_filter = ['region']
    readonly_fields = ['name','region','subregion','iso3']
    fields = ['poly', ('iso3','name', 'region','subregion')]
    
@admin.register(Continent)
class ContinentAdmin(MappingAbstract):
    list_display = ['name','site_count']
    readonly_fields = ['name']
    fields = ['name','poly']

@admin.register(Political)
class PoliticalAdmin(MappingAbstract):
    list_display = ['name','iso','site_count']
    readonly_fields = ['iso','name']
    search_fields = ['iso','name']
    fields = ['poly',('iso','name')]



@admin.register(Ocean)
class Ocean(MappingAbstract):
    list_display = ['name','site_count']
    search_fields = ['name']
    readonly_fields = ['name']
    fields = ['poly','name']

