from rest_framework import serializers
from well_logs import models
from api.v1.serialize import SimpleSite


class LogSerializerMixin(serializers.ModelSerializer):

    # id = serializers.ReadOnlyField()
    data_count = serializers.IntegerField()
    depth_upper = serializers.FloatField()
    depth_lower = serializers.FloatField()
    site = SimpleSite()

    class Meta:
        exclude = ['source_id','added']
        datatables_always_serialize = ('id',)


class NestedConductivity(serializers.ModelSerializer):
    class Meta:
        model = models.Conductivity
        exclude = ['id','log']


class ConductivitySerializer(LogSerializerMixin):
    data = NestedConductivity(many=True)

    class Meta(LogSerializerMixin.Meta):
        model = models.ConductivityLog


class NestedHP(serializers.ModelSerializer):
    class Meta:
        model = models.HeatProduction
        exclude = ['id','log']


class HeatProductionSerializer(LogSerializerMixin):
    data = NestedHP(many=True)

    class Meta(LogSerializerMixin.Meta):
        model = models.HeatProductionLog


class NestedTemp(serializers.ModelSerializer):
    class Meta:
        model = models.Temperature
        fields = ['depth','value','uncertainty']
        # exclude = ['id','log']


class TemperatureSerializer(LogSerializerMixin):
    data = NestedTemp(many=True)

    class Meta(LogSerializerMixin.Meta):
        model = models.TemperatureLog
