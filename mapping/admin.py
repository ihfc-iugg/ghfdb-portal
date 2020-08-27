from django.contrib.gis import admin
from .models import Country, Continent, Sea, Margin, Basin, Political
from django.db.models import Count

class MappingAbstract(admin.GeoModelAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(sites__isnull=False).annotate(
            _number_of_sites=Count("sites")).order_by('-_number_of_sites')

    def number_of_sites(self,obj):
        return obj._number_of_sites
    number_of_sites.admin_order_field = '_number_of_sites'

@admin.register(Country)
class CountryAdmin(MappingAbstract):
    list_display = ['name','region','subregion','number_of_sites']
    search_fields = ['name','region','subregion',]
    list_filter = ['region']

    fields = [
        'name',
        ('lat','lon'),
        'poly',
        'fips',
        ('iso2','iso3','un'),
        'area',
        ('region','subregion'),
        'pop2005',
    ]
    
@admin.register(Continent)
class ContinentAdmin(MappingAbstract):
    list_display = ['name','number_of_sites']
    fields = [
        'name',
        'poly',
        ('shape_area','sqkm'),
    ]

@admin.register(Sea)
class SeaAdmin(MappingAbstract):
    list_display = ['name','number_of_sites']
    fields = [
        'name',
        'poly',
        ('longitude','latitude'),
        ('min_x','max_x'),
        ('min_y','max_y'),
    ]

@admin.register(Basin)
class BasinAdmin(admin.GeoModelAdmin):
    list_display = ['name','region','province','max_fill','exploration_status','location','sub_regime','sub_regime_group','petsys_status']
    search_fields = ['name','region','province',]
    list_filter = ['exploration_status','petsys_status']

    fields = [
        'name',
        'poly',
        'region',
        'province'
    ]

@admin.register(Political)
class PoliticalAdmin(admin.GeoModelAdmin):
    list_display = ['name','territory','sovereign','area_km2',]
    search_fields = ['name','territory','sovereign',]

    fields = [
        'name',
        'poly',
    ]

@admin.register(Margin)
class MarginAdmin(admin.GeoModelAdmin):
    list_display = ['id','area','perimetre','superficie']
    # fields = [
    #     'name',
    #     'poly',
    #     ('longitude','latitude'),
    #     ('min_x','max_x'),
    #     ('min_y','max_y'),
    # ]


    # def get_queryset(self, request):
    #     queryset = super().get_queryset(request)
    #     queryset = queryset.annotate(
    #         _number_of_sites=Count("sites"),
    #         )
    #     return queryset

    # def number_of_sites(self,obj):
    #     return obj._number_of_sites
    # number_of_sites.admin_order_field = '_number_of_sites'