from django.contrib.gis import admin
from .models import Country, Continent, Sea, Margin, Basin, Political, Province
from django.db.models import Count, Avg, Q
from django.db.models.functions import Coalesce

class MappingAbstract(admin.GeoModelAdmin):
    def get_queryset(self, request):
        return (super().get_queryset(request)
        # .filter(sites__isnull=False)
        .annotate(
            _number_of_sites=Count("sites"),
            _ave_heat_flow=Avg(
                Coalesce('sites__intervals__heat_flow_corrected',
                'sites__intervals__heat_flow_uncorrected')
                )
            )
        .order_by('-_number_of_sites')
        )

    def ave_heat_flow(self,obj):
        return obj._ave_heat_flow
    ave_heat_flow.admin_order_field = '_ave_heat_flow'

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
class BasinAdmin(MappingAbstract):
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
class PoliticalAdmin(MappingAbstract):
    list_display = ['name','territory','sovereign','area_km2',]
    search_fields = ['name','territory','sovereign',]

    fields = [
        'name',
        'poly',
    ]

@admin.register(Province)
class ProvinceAdmin(MappingAbstract):
    list_display = ['id','name','type','group','juvenile_age_min','juvenile_age_max','thermotectonic_age_min','thermotectonic_age_max','last_orogen','continent','plate','number_of_sites','ave_heat_flow']
    search_fields = ['name','type','group','continent']
    list_filter = ['continent','type','group','last_orogen','plate']
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