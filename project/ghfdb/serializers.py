from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers


@extend_schema_serializer(examples=[OpenApiExample(name="GHFDB Column Metadata", value={})])
class MyJSONSchemaSerializer(serializers.Serializer):
    class Meta:
        ref_name = "MyJSONSchema"
