# from django.contrib.auth.models import User, Group
from rest_framework import serializers
from thermoglobe import models
from publications import models as pub_models


class SimpleSite(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    data_counts = serializers.SerializerMethodField()

    class Meta:
        model = models.Site
        fields = ['url','id','site_name','latitude','longitude','elevation','description','data_counts']
        # exclude = ['reference','slug','geom','continent','country','political','province','sea','crustal_thickness','seamount_distance','outcrop_distance']

    def get_data_counts(self,obj):
        return obj.data_counts()

class Site(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    data_counts = serializers.SerializerMethodField()
    class Meta:
        model = models.Site
        exclude = ['reference','slug',]
        read_only_fields = ['continent','country','political','province','sea','crustal_thickness','seamount_distance','outcrop_distance']

    def get_data_counts(self,obj):
        return obj.data_counts()

class Publication(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = pub_models.Publication
        exclude = ['verified_by','bibtex','pdf',]

class Interval(serializers.HyperlinkedModelSerializer):
    site = SimpleSite(read_only=True)
    heat_flow = serializers.FloatField()
    heat_flow_uncertainty = serializers.FloatField()
    gradient = serializers.FloatField()
    gradient_uncertainty = serializers.FloatField()

    # _heat_flow = HeatFlow()
    _corrected = serializers.SerializerMethodField()
    _uncorrected = serializers.SerializerMethodField()

    class Meta:
        model = models.Interval
        # fields = ['site','reference','heat_flow','gradient','_heat_flow']
        exclude = ['global_by','heat_flow_corrected','heat_flow_corrected_uncertainty','gradient_corrected','gradient_corrected_uncertainty','heat_flow_uncorrected','heat_flow_uncorrected_uncertainty','gradient_uncorrected','gradient_uncorrected_uncertainty']

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
    site = SimpleSite(read_only=True)

    class Meta:
        model = models.Conductivity
        exclude = ['date_added']

class HeatProduction(serializers.HyperlinkedModelSerializer):
    site = SimpleSite(read_only=True)

    class Meta:
        model = models.HeatProduction
        exclude = ['date_added']


class Temperature(serializers.HyperlinkedModelSerializer):
    site = SimpleSite(read_only=True)
    
    class Meta:
        model = models.Temperature
        exclude = ['date_added']



