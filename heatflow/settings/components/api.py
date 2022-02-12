REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables_editor.pagination.DatatablesPageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework_datatables_editor.filters.DatatablesFilterBackend',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'api.utils.BrowsableAPIRenderer',
        'rest_framework_datatables_editor.renderers.DatatablesRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ]
    # 'DEFAULT_SCHEMA_CLASS': 'rest_framework_gis.schema.GeoFeatureAutoSchema',
}

SERIALIZATION_MODULES = {
    "geojson": "django.contrib.gis.serializers.geojson", 
 }