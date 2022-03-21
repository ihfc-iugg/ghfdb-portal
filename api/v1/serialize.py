# from django.contrib.auth.models import User, Group
from rest_framework import serializers
from thermoglobe.models import Site, Interval
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from django.shortcuts import get_object_or_404
from well_logs import models
# from well_logs.api.serialize import TemperatureSerializer
from publications.api.serialize import PublicationSerializer

class SimpleSite(serializers.HyperlinkedModelSerializer):
    web_url = serializers.URLField(source='get_absolute_url', read_only=True)

    class Meta:
        model = Site
        fields = ['web_url','id','site_name','latitude','longitude']


class DataSerializer(serializers.Serializer):

    interval_count = serializers.SerializerMethodField()
    # intervals = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    temperature_log_count = serializers.SerializerMethodField()
    # temperature_logs = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    heat_production_log_count = serializers.SerializerMethodField()
    # heat_production_logs = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    conductivity_log_count = serializers.SerializerMethodField()
    # conductivity_logs = serializers.PrimaryKeyRelatedField(many=True, read_only=True)



    def get_site_count(self, obj):
        return obj.sites.count()

    def get_reference_count(self, obj):
        return obj.reference.count()

    def get_temperature_log_count(self, obj):
        return obj.temperature_logs.count()

    def get_heat_production_log_count(self, obj):
        return obj.heat_production_logs.count()

    def get_conductivity_log_count(self, obj):
        return obj.conductivity_logs.count()

    def get_interval_count(self, obj):
        return obj.intervals.count()




class Site(serializers.HyperlinkedModelSerializer, DataSerializer):
    website = serializers.SerializerMethodField()
    reference_count = serializers.SerializerMethodField()
    references = serializers.PrimaryKeyRelatedField(source='reference', many=True, read_only=True)

    class Meta:
        model = Site
        datatables_always_serialize = ('id',)

        fields = ['id',
        'site_name', 
        'latitude', 
        'longitude', 
        "elevation",  
        "well_depth", 
        "cruise", 
        "seafloor_age",
        "sediment_thickness", 
        "sediment_thickness_type", 
        "bottom_water_temp", 
        "year_drilled", 
        "description",
        'interval_count',
        'intervals',
        'temperature_log_count',
        'temperature_logs',
        'conductivity_log_count',
        'conductivity_logs',
        'heat_production_log_count',
        'heat_production_logs',
        'references',
        'reference_count',       
        "website",
        ]



    def get_website(self, obj):
        request = self.context.get('request')
        uri = request.build_absolute_uri(obj.get_absolute_url())
        return f"<a href='{uri}'>{obj.site_name}</a>"


class Interval(serializers.HyperlinkedModelSerializer):
    website = serializers.SerializerMethodField()
    site = SimpleSite(read_only=True, style={'base_template': 'input.html'})
    heat_flow = serializers.FloatField()
    heat_flow_uncertainty = serializers.FloatField()
    gradient = serializers.FloatField()
    gradient_uncertainty = serializers.FloatField()

    _corrected = serializers.SerializerMethodField()
    _uncorrected = serializers.SerializerMethodField()

    class Meta:
        model = Interval
        fields = [
            'id',
            'site',
            "depth_min",
            "depth_max",
            "heat_flow",
            "heat_flow_uncertainty",
            "reliability",
            "gradient",
            "gradient_uncertainty",
            "num_temp",
            "temp_method",
            "cond_ave",
            "cond_unc",
            "num_cond",
            "cond_method",
            "heat_prod",
            "heat_prod_unc",
            "num_heat_prod",
            "heat_prod_method",
            "tilt",
            "comment",
            # "source",
            # "global_flag",
            # "global_reason",
            # "date_added",
            "reference",
            '_corrected',
            '_uncorrected',
            'website',
        ]

        datatables_always_serialize = ('id',)

    def get_website(self, obj):
        request = self.context.get('request')
        uri = request.build_absolute_uri(obj.site.get_absolute_url())
        return f"<a href='{uri}'>{obj.site.site_name}</a>"

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


class PublicationSerializer(PublicationSerializer, DataSerializer):

    site_count = serializers.SerializerMethodField()
    sites = serializers.PrimaryKeyRelatedField(many=True, read_only=True)




