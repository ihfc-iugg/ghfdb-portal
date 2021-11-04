from .models import Country, Continent, Sea, Political, Province
from thermoglobe.models import Site

def countries(force=False):
    """update countries in database

    Args:
        force (bool, optional): if True will update all entries, false will update only entries without an existing country entry. Defaults to False.
    """
    # qs = Country.objects.all()if
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

def political():
    for region in Political.objects.all():
        sites = Site.objects.filter(geom__within=region.poly)
        sites.update(political=region)

def province():
    for province in Province.objects.all():
        sites = Site.objects.filter(geom__within=province.poly)
        sites.update(province=province)