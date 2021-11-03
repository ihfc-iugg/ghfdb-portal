# from django.contrib.auth.models import User, Group
from rest_framework import serializers
from thermoglobe import models
from publications import models as pub_models

class Site(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Site
        # fields = "__all__"
        exclude = ['reference','geom','slug']

class Publication(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = pub_models.Publication
        exclude = ['verified_by','bibtex','pdf',]

class Interval(serializers.HyperlinkedModelSerializer):
    site = Site(read_only=True)
    reference = Publication(read_only=True)

    class Meta:
        model = models.Interval
        exclude = ['global_by']

class Conductivity(serializers.HyperlinkedModelSerializer):
    site = Site(read_only=True)
    reference = Publication(read_only=True)

    class Meta:
        model = models.Conductivity
        fields = "__all__"

class HeatProduction(serializers.HyperlinkedModelSerializer):
    site = Site(read_only=True)
    reference = Publication(read_only=True)

    class Meta:
        model = models.HeatProduction
        fields = "__all__"

class Temperature(serializers.HyperlinkedModelSerializer):
    site = Site(read_only=True)
    reference = Publication(read_only=True)
    
    class Meta:
        model = models.Temperature
        fields = "__all__"


