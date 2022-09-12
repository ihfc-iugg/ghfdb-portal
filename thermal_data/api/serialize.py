from rest_framework import serializers
from well_logs import models
from api.v1.serialize import Site

class LogSerializerMixin(serializers.HyperlinkedModelSerializer):

    data_count = serializers.IntegerField()
    depth_upper = serializers.FloatField()
    depth_lower = serializers.FloatField()
    site = Site()

    class Meta:
        exclude = ['source_id','date_added']
        datatables_always_serialize = ('id',)

class ConductivityData(serializers.ModelSerializer):
    class Meta:
        model = models.Conductivity
        exclude = ['id','log']

class ConductivityLogs(LogSerializerMixin):

    class Meta(LogSerializerMixin.Meta):
        model = models.ConductivityLog

class TemperatureLogs(LogSerializerMixin):

    class Meta(LogSerializerMixin.Meta):
        model = models.TemperatureLog

class TemperatureData(serializers.ModelSerializer):

    class Meta:
        model = models.Temperature
        exclude = ['id','log']


