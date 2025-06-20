from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers


@extend_schema_serializer(examples=[{"name": "GHFDB Column Metadata", "value": {}}])
class MyJSONSchemaSerializer(serializers.Serializer):
    class Meta:
        ref_name = "MyJSONSchema"
