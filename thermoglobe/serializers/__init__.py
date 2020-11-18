from django.core.serializers import register_serializer

register_serializer('json-no-uescape', 'serializers.json_no_uescape')