from .models import Country, Continent, Sea, Basin, Political
from thermoglobe.models import Site

def countries():
    for country in Country.objects.all():
        sites = Site.objects.filter(geom__within=country.poly)
        sites.update(country=country)

def continents():
    for continent in Continent.objects.all():
        sites = Site.objects.filter(geom__within=continent.poly)
        sites.update(continent=continent)

def seas():
    for sea in Sea.objects.all():
        sites = Site.objects.filter(geom__within=sea.poly)
        sites.update(sea=sea)

def basins():
    for basin in Basin.objects.all():
        sites = Site.objects.filter(geom__within=basin.poly)
        sites.update(CGG_basin=basin)

def political():
    for region in Political.objects.all():
        sites = Site.objects.filter(geom__within=region.poly)
        sites.update(political=region)