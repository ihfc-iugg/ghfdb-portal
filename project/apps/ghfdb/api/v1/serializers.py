from ghfdb.models import Interval
from rest_framework import serializers


class Interval(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Interval
        fields = "__all__"
        datatables_always_serialize = ("id",)
