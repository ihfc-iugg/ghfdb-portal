from .models import Country, Continent, Sea, Basin
from thermoglobe.models import Site

def update_countries():
    for country in Country.objects.all():
        sites = Site.objects.filter(geom__within=country.poly)
        sites.update(country=country)

def update_continents():
    for continent in Continent.objects.all():
        sites = Site.objects.filter(geom__within=continent.poly)
        sites.update(continent=continent)

def update_seas():
    for sea in Sea.objects.all():
        sites = Site.objects.filter(geom__within=sea.poly)
        sites.update(sea=sea)

def update_basins():
    for basin in Basin.objects.all():
        sites = Site.objects.filter(geom__within=basin.poly)
        sites.update(CGG_basin=basin)