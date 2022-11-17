from django.utils.translation import gettext_lazy as _
from geoluminate.settings import *
from geoluminate.settings.components.django import (
    ALLOWED_HOSTS,
    INSTALLED_APPS,
    MIDDLEWARE,
)

SITE_NAME = META_SITE_NAME = 'World Heat Flow Database'
EMAIL_DOMAIN = "@heatflow.world"
ADMINS = MANAGERS = [('Sam', 'jennings@gfz-potsdam.de')]

# UNCOMMENT TO COLLECTSTATIC TO AWS S3
# STATICFILES_STORAGE = 'project.storage_backends.StaticStorage'
# STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_STATIC_LOCATION}/"

# enter additional domains or ip addresses of allowed hosts here.
# 127.0.0.1 and localhost are already included
ALLOWED_HOSTS.extend([])

INSTALLED_APPS.extend([
    'newsletter',
    'rest_framework',
    'rest_framework_gis',
    "drf_spectacular",
    'rest_framework_datatables_editor',
    "menu",
    "django_select2",
    "drf_auto_endpoint",
    'import_export',
    # 'import_export_celery',
    'simple_history',
    "treewidget",
    'datacite',
    'geoluminate.gis',
    'datatables',


    # GHFDB Apps
    "well_logs",
    "global_tectonics",
    'earth_science',
    'database',
    'thermal_data',
    'review',
    "research_organizations",

    # "debug_toolbar",
])


MIDDLEWARE.extend([
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    # 'author.middlewares.AuthorDefaultBackendMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
])

EARTH_MATERIALS_INCLUDE = [
    'Igneous rock and sediment',
    'Metamorphic rock',
    'Sediment and sedimentary rock'
]

TREEWIDGET_SETTINGS = {
    'search': True,
    # 'show_buttons': True
    "can_add_related": False,
}

TREEWIDGET_TREEOPTIONS = {
    "core": {
        "themes": {
            "variant": "large",
            "icons": False,
        },
    },
    'search': {
        # 'fuzzy':True,
        'show_only_matches': True,
    },
    'checkbox': {
        'three_state': False,
    },
    "plugins": ["checkbox"]
}

DEFAULT_FROM_EMAIL = f'info{EMAIL_DOMAIN}'

CACHES = {
    # … default cache config and others
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
    "select2": {
        # "BACKEND": "django_redis.cache.RedisCache",
        # "LOCATION": "redis://127.0.0.1:6379/2",
        # "OPTIONS": {
        #     "CLIENT_CLASS": "django_redis.client.DefaultClient",
        # }
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        'LOCATION': 'select2',
    }
}

# Tell select2 which cache configuration to use:
SELECT2_CACHE_BACKEND = "select2"

SELECT2_CSS = [
    "https://cdn.jsdelivr.net/npm/select2@4.0.13/dist/css/select2.min.css",
    "https://cdn.jsdelivr.net/npm/select2-bootstrap-5-theme@1.3.0/dist/select2-bootstrap-5-theme.min.css",
]

SELECT2_THEME = 'bootstrap-5'

# THUMBNAIL_DEFAULT_STORAGE = 'project.storage_backends.PublicMediaStorage'
# PRIVATE_FILE_STORAGE = DEFAULT_FILE_STORAGE = 'project.storage_backends.PrivateMediaStorage'

REST_FRAMEWORK = {
    "HTML_SELECT_CUTOFF": 10,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'geoluminate.api.throttling.AnonBurstRate',
        'geoluminate.api.throttling.AnonSustainedRate',
        'geoluminate.api.throttling.UserBurstRate'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon_burst': '4/second',
        'anon_sustained': '30/minute',
        'user_burst': '25/second'
    },
    'DEFAULT_PERMISSION_CLASSES': [
        "geoluminate.access_policies.CoreAccessPolicy",
    ],
    'DEFAULT_RENDERER_CLASSES': [
        "drf_orjson_renderer.renderers.ORJSONRenderer",
        "geoluminate.api.renderers.GeoJSONRenderer",
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_csv.renderers.PaginatedCSVRenderer'
    ],
    # 'DEFAULT_FILTER_BACKENDS': (

    # ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,

    'DEFAULT_PARSER_CLASSES': [
        'drf_orjson_renderer.parsers.ORJSONParser',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_METADATA_CLASS': 'datatables.metadata.DatatablesAutoMetadata',
}

GRAPH_MODELS = {
    'app_labels': ["database", "thermal_data", "publications", "well_logs", "crossref"],
    "exclude_models": ['PublicationAbstract', 'UUIDTaggedItem', 'HeatFlowAbstract', 'IntervalAbstract', 'HistoricalSite', 'HistoricalInterval', 'AbstractLog', 'ChoiceAbstract', 'AuthorAbstract'],
    'all_applications': False,
    'group_models': True,
    # 'hide_edge_labels': True,
    # "hide_relations_from_fields":True,
    # 'skip_check':True,
}

CELERY_BROKER_URL = "redis://localhost:6379"
CELERY_RESULT_BACKEND = "redis://localhost:6379"

IMPORT_EXPORT_CELERY_INIT_MODULE = "project.celery"

IMPORT_EXPORT_CELERY_MODELS = {
    "Winner": {
        'app_label': 'database',
        'model_name': 'Site',
        # 'resource': SiteResource,  # Optional
    }
}

DASHBOARDS = {
    'user': 'user.dashboard.UserDashboard',
}

GEOLUMINATE_DATABASE = 'database.HeatFlow'
GEOLUMINATE_API_ROUTERS = [
    'geoluminate.gis.urls.router',
    'literature.api.urls.router',
    'literature.api.urls.lit_router',
]
