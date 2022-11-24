from rest_framework import serializers
from database.models import Interval


class Interval(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Interval
        fields = "__all__"
        datatables_always_serialize = ('id',)
