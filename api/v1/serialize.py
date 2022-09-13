from rest_framework import serializers
from database.models import Site, Interval
# from well_logs.api.serialize import TemperatureSerializer
from publications.api.serialize import PublicationSerializer
from api.utils import FasterGeoFeatureSerializer


class FeatureSerializer(FasterGeoFeatureSerializer):

    class Meta:
        model = Site
        as_geom = 'geometry'
        geo_field = 'geom'
        exclude = ['references','date_added','lat','lng','country','continent','plate','province','ocean','political','last_modified']


class Site(serializers.HyperlinkedModelSerializer):
    id = serializers.CharField() #required for datatables

    class Meta:
        model = Site
        datatables_always_serialize = ('id',)
        exclude = ['geom']


class Interval(serializers.HyperlinkedModelSerializer):
    site = Site(read_only=True, style={'base_template': 'input.html'})

    class Meta:
        model = Interval
        # fields = (*[f.name for f in Interval._meta.get_fields()])
        fields = "__all__"
        datatables_always_serialize = ('id',)


class PublicationSerializer(PublicationSerializer):

    # site_count = serializers.SerializerMethodField()
    sites = serializers.PrimaryKeyRelatedField(many=True, read_only=True)


