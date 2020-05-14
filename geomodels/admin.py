from django.contrib import admin
from .models import Basin, Formation, TectonicEnvironment, GeologicalProvince, GeologicalUnit, SedimentThickness
from django.db.models import F, Count


# Register your models here.
class AdminMixin(admin.ModelAdmin):

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _sites=Count("site", distinct=True),)   
            
        return queryset

    def sites(self,obj):
        return obj._sites
    sites.admin_order_field = '_sites'

@admin.register(Basin)
class BasinAdmin(admin.ModelAdmin):
    list_display = ['name','as_basin','as_sub_basin']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _basin=Count("basin", distinct=True),
            _sub_basin=Count("sub_basin", distinct=True),
            )   
            
        return queryset

    def as_basin(self,obj):
        return obj._basin
    as_basin.admin_order_field = '_basin'

    def as_sub_basin(self,obj):
        return obj._sub_basin
    as_sub_basin.admin_order_field = '_sub_basin'

@admin.register(Formation)
class FormationAdmin(AdminMixin):
    pass

@admin.register(TectonicEnvironment)
class TectonicEnvironmentAdmin(AdminMixin):
    pass

@admin.register(GeologicalProvince)
class GeologicalProvinceAdmin(AdminMixin):
    pass

# @admin.register(GeologicalUnit)
# class GeologicalUnitAdmin(AdminMixin):
#     pass


