# from django.contrib.auth.models import User, Group
from rest_framework import serializers
from thermoglobe import models
from publications import models as pub_models
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from django.shortcuts import get_object_or_404

class GeoSite(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Site
        fields = ['url','latitude','longitude',]

class GeoSite2(serializers.HyperlinkedModelSerializer,GeoFeatureModelSerializer):
    # link = serializers.URLField(source='get_absolute_url', read_only=True)
    class Meta:
        model = models.Site
        geo_field = 'geom'
        fields = ['url','site_name',]

    def get_data_counts(self,obj):
        return obj.data_counts()

class SimpleSite(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    web_url = serializers.URLField(source='get_absolute_url', read_only=True)
    data_counts = serializers.SerializerMethodField()

    class Meta:
        model = models.Site
        fields = ['url','web_url','id','site_name','latitude','longitude','elevation','description','data_counts']
        exclude = ['reference','slug','geom','continent','country','political','province','sea','crustal_thickness','seamount_distance','outcrop_distance']

    def get_data_counts(self,obj):
        return obj.data_counts()


class Site(serializers.HyperlinkedModelSerializer):
    # id = serializers.ReadOnlyField()
    id = serializers.CharField(read_only=True)
    web_url = serializers.URLField(source='get_absolute_url', read_only=True)
    # data_counts = serializers.SerializerMethodField()


    class Meta:
        model = models.Site
        exclude = ['reference','slug','geom','continent','country','political','province','ocean','plate','crustal_thickness','seamount_distance','outcrop_distance']

        # read_only_fields = ['continent','country','political','province','crustal_thickness','seamount_distance','outcrop_distance']

    def to_internal_value(self, data):
        return get_object_or_404(models.Site, pk=data['id'])

    # def get_data_counts(self,obj):
    #     return obj.data_counts()


class Publication(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = pub_models.Publication
        exclude = ['verified_by','bibtex','pdf',]


class Interval(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    site = SimpleSite(read_only=True, style={'base_template': 'input.html'})
    heat_flow = serializers.FloatField()
    heat_flow_uncertainty = serializers.FloatField()
    gradient = serializers.FloatField()
    gradient_uncertainty = serializers.FloatField()

    # _heat_flow = HeatFlow()
    _corrected = serializers.SerializerMethodField()
    _uncorrected = serializers.SerializerMethodField()

    class Meta:
        model = models.Interval
        exclude = ['global_by','heat_flow_corrected','heat_flow_corrected_uncertainty','gradient_corrected','gradient_corrected_uncertainty','heat_flow_uncorrected','heat_flow_uncorrected_uncertainty','gradient_uncorrected','gradient_uncorrected_uncertainty']
        datatables_always_serialize = ('id',)

    def get__corrected(self, obj):
        return dict(
            heat_flow=obj.heat_flow_corrected,
            heat_flow_uncertainty=obj.heat_flow_corrected_uncertainty,
            gradient=obj.gradient_corrected,
            gradient_uncertainty=obj.gradient_corrected_uncertainty,
        )

    def get__uncorrected(self, obj):
        return dict(
            heat_flow=obj.heat_flow_uncorrected,
            heat_flow_uncertainty=obj.heat_flow_uncorrected_uncertainty,
            gradient=obj.gradient_uncorrected,
            gradient_uncertainty=obj.gradient_uncorrected_uncertainty,
        )


class Conductivity(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    site = SimpleSite(read_only=True)

    class Meta:
        model = models.Conductivity
        exclude = ['date_added']
        datatables_always_serialize = ('id',)


class HeatProduction(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    site = SimpleSite(read_only=True)

    class Meta:
        model = models.HeatProduction
        exclude = ['date_added']
        datatables_always_serialize = ('id',)

    DT_RowAttr = serializers.SerializerMethodField()

    @staticmethod
    def get_DT_RowAttr(album):
        return {'data-pk': album.pk}


class Temperature(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    site = SimpleSite(read_only=True)
    
    class Meta:
        model = models.Temperature
        exclude = ['date_added']
        datatables_always_serialize = ('id',)



