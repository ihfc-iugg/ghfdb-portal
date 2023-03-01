from django.contrib import admin
from django.db.models import Count, F, Max, Min
from django.utils.translation import gettext as _
from geoluminate.contrib.admin.mixins import BaseAdmin
from geoluminate.contrib.gis.db_functions import Lat, Lon
from import_export.admin import ImportExportActionModelAdmin
from well_logs.models import Log

from .models import ConductivityLog, Temperature, TemperatureLog
from .resources import ConductivityResource, TempResource

admin.site.unregister(Log)


class AbstractAdmin(BaseAdmin, ImportExportActionModelAdmin):

    list_filter = ["source", "method"]
    # autocomplete_fields = ["site", "reference"]
    search_fields = ["site__name", "_lat", "_lon", "id"]
    readonly_fields = ["added", "modified"]
    fieldsets = [
        (
            "Site",
            {
                "fields": [
                    "site",
                ]
            },
        ),
        (
            "Log Information",
            {
                "fields": [
                    "year_logged",
                    "method",
                    "comment",
                ]
            },
        ),
        (
            "Data Source",
            {
                "fields": [
                    "reference",
                    ("source", "source_id"),
                    "operator",
                ]
            },
        ),
        (
            "Additional Information",
            {
                "fields": [
                    "added",
                ]
            },
        ),
    ]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("site")
            .prefetch_related("data")
            .annotate(
                _name=F("site__name"),
                _lat=Lat("site__geom"),
                _lon=Lon("site__geom"),
                _data_count=Count("data"),
                _min_depth=Min("data__depth"),
                _max_depth=Max("data__depth"),
            )
        )

    def lat(self, obj):
        return obj._lat

    def lon(self, obj):
        return obj._lon

    def data_count(self, obj):
        return obj._data_count

    data_count.admin_order_field = "_data_count"
    data_count.short_description = _("count (n)")

    def min_depth(self, obj):
        return obj._min_depth

    min_depth.admin_order_field = "_min_depth"
    min_depth.short_description = _("upper depth (m)")

    def max_depth(self, obj):
        return obj._max_depth

    max_depth.admin_order_field = "_max_depth"
    max_depth.short_description = _("lower depth (m)")


@admin.register(TemperatureLog)
class TemperatureLogAdmin(AbstractAdmin):

    resource_class = TempResource

    list_display = [
        "id",
        "name",
        "lat",
        "lon",
        "min_depth",
        "max_depth",
        "data_count",
        "start_time",
        "finish_time",
        "method",
        "correction",
        "circ_time",
        "lag_time",
        "reference",
        "operator",
        "source",
    ]

    fieldsets = [
        (
            "Site",
            {
                "fields": [
                    "site",
                ]
            },
        ),
        (
            "Log Information",
            {
                "fields": [
                    ("circ_time", "lag_time"),
                    "method",
                    "correction",
                    "comment",
                ]
            },
        ),
        (
            "Data Source",
            {
                "fields": [
                    "reference",
                    ("source", "source_id"),
                    "operator",
                ]
            },
        ),
        (
            "Additional Information",
            {
                "fields": [
                    "added",
                ]
            },
        ),
    ]


@admin.register(ConductivityLog)
class ConductivityAdmin(AbstractAdmin):
    resource_class = ConductivityResource
    list_display = [
        "edit",
        "name",
        "lat",
        "lon",
        "min_depth",
        "max_depth",
        "data_count",
        "start_time",
        "finish_time",
        "method",
        "reference",
        "operator",
        "source",
    ]


@admin.register(Temperature)
class ConductivityAdmin(admin.ModelAdmin):
    list_display = ["depth", "value"]
