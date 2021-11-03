from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from api import serialize
from thermoglobe.models import Site, Interval, Conductivity, HeatProduction, Temperature
from publications.models import Publication
from api.paginators import DataTablesPaginator
from django_filters.rest_framework import DjangoFilterBackend

class SiteViewSet(viewsets.ModelViewSet):
    """API endpoint to request a set of ThermoGlobe sites."""
    queryset = Site.objects.all()
    serializer_class = serialize.Site

class PublicationViewSet(viewsets.ModelViewSet):
    """API endpoint to request a set of ThermoGlobe publications."""
    queryset = Publication.objects.all()
    serializer_class = serialize.Publication

class HeatFlowViewSet(viewsets.ModelViewSet):
    """API endpoint to request a set of heat flow intervals."""
    queryset = Interval.heat_flow.all()
    serializer_class = serialize.Interval
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DataTablesPaginator
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['reference']

class GradientViewSet(viewsets.ModelViewSet):
    """API endpoint to request a set of thermal gradient intervals."""
    queryset = Interval.gradient.all()
    serializer_class = serialize.Interval
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DataTablesPaginator
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['reference']

class ConductivityViewSet(viewsets.ModelViewSet):
    """API endpoint to request a set of thermal conductivity measurements."""
    queryset = Conductivity.objects.all()
    serializer_class = serialize.Conductivity
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DataTablesPaginator
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['reference']

class HeatProductionViewSet(viewsets.ModelViewSet):
    """API endpoint to request a set of heat production measurements."""
    queryset = HeatProduction.objects.all()
    serializer_class = serialize.HeatProduction
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DataTablesPaginator
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['reference']

class TemperatureViewSet(viewsets.ModelViewSet):
    """API endpoint to request a set of temperature measurements."""
    queryset = Temperature.objects.all()
    serializer_class = serialize.Temperature
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DataTablesPaginator
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['reference']