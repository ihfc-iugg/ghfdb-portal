from rest_framework_gis.filters import DistanceToPointOrderingFilter
from rest_framework import serializers
from collections import OrderedDict
from rest_framework_gis.serializers import GeoFeatureModelSerializer

class DistanceToPointOrderingFilter(DistanceToPointOrderingFilter):

    def get_schema_operation_parameters(self, view):
        params = super().get_schema_operation_parameters(view)
        params.append(
            {
                "name": self.order_param,
                "required": False,
                "in": "query",
                "description": "",
                "schema": {
                    "type": "enum",
                    "items": {"type": "string", "enum": ["asc", "desc"]},
                    "example": "desc",
                },
                "style": "form",
                "explode": False,
            }
        )
        return params

class GeomField(serializers.CharField):

    def to_representation(self, value):
        return eval(super().to_representation(value))

class FasterGeoFeatureSerializer(GeoFeatureModelSerializer):

    def to_representation(self, instance):
        """
        Serialize objects -> primitives.
        """
        # prepare OrderedDict geojson structure
        feature = OrderedDict()

        # keep track of the fields being processed
        processed_fields = set()

        # optional id attribute
        if self.Meta.id_field:
            field = self.fields[self.Meta.id_field]
            value = field.get_attribute(instance)
            feature["id"] = field.to_representation(value)
            processed_fields.add(self.Meta.id_field)

        # required type attribute
        # must be "Feature" according to GeoJSON spec
        feature["type"] = "Feature"

        # required geometry attribute
        # MUST be present in output according to GeoJSON spec
        field = self.fields[self.Meta.geo_field]
        geo_value = field.get_attribute(instance)
        # feature["geometry"] = field.to_representation(geo_value)
        feature["geometry"] = eval(getattr(instance,self.Meta.as_geom))
        processed_fields.add(self.Meta.geo_field)

        # # Bounding Box
        # # if auto_bbox feature is enabled
        # # bbox will be determined automatically automatically
        if self.Meta.auto_bbox and geo_value:
            feature["bbox"] = geo_value.extent
        # otherwise it can be determined via another field
        elif self.Meta.bbox_geo_field:
            field = self.fields[self.Meta.bbox_geo_field]
            value = field.get_attribute(instance)
            feature["bbox"] = value.extent if hasattr(value, 'extent') else None
            processed_fields.add(self.Meta.bbox_geo_field)

        # the list of fields that will be processed by get_properties
        # we will remove fields that have been already processed
        # to increase performance on large numbers
        fields = [
            field_value
            for field_key, field_value in self.fields.items()
            if field_key not in processed_fields
        ]

        # GeoJSON properties
        feature["properties"] = self.get_properties(instance, fields)

        return feature