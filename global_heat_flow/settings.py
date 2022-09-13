import os
from core.settings import *
from django.utils.translation import gettext_lazy as _

SITE_NAME = 'World Heat Flow Database'
EMAIL_DOMAIN = "@thermoglobe.app"
APP_NAME = 'global_heat_flow'
ADMINS = MANAGERS = [('Sam','jennings@gfz-potsdam.de')]

# UNCOMMENT TO COLLECTSTATIC TO AWS S3
# STATICFILES_STORAGE = f{APP_NAME}.storage_backends.StaticStorage'
# STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_STATIC_LOCATION}/"

ALLOWED_HOSTS += ['thermoglobe.herokuapp.com','www.thermoglobe.app','thermoglobe.app',"139.17.115.184"]

INSTALLED_APPS = [

    'core',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'grappelli.dashboard',
    'grappelli',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'django_cleanup.apps.CleanupConfig',
    'authentication',
    'user',
    'django.contrib.gis',
    'django.contrib.humanize',
    'django.contrib.admindocs',
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.orcid",
    "invitations",
    'organizations',
    'cms',
    'menus',
    'sekizai',
    'treebeard',

    'djangocms_text_ckeditor',
    'filer',
    'easy_thumbnails',
    'djangocms_file',
    'djangocms_icon',
    'djangocms_link',
    'djangocms_picture',
    'djangocms_bootstrap5',
    'djangocms_bootstrap5.contrib.bootstrap5_alerts',
    'djangocms_bootstrap5.contrib.bootstrap5_badge',
    'djangocms_bootstrap5.contrib.bootstrap5_card',
    'djangocms_bootstrap5.contrib.bootstrap5_carousel',
    'djangocms_bootstrap5.contrib.bootstrap5_collapse',
    'djangocms_bootstrap5.contrib.bootstrap5_content',
    'djangocms_bootstrap5.contrib.bootstrap5_grid',
    'djangocms_bootstrap5.contrib.bootstrap5_jumbotron',
    'djangocms_bootstrap5.contrib.bootstrap5_link',
    'djangocms_bootstrap5.contrib.bootstrap5_listgroup',
    'djangocms_bootstrap5.contrib.bootstrap5_media',
    'djangocms_bootstrap5.contrib.bootstrap5_picture',
    'djangocms_bootstrap5.contrib.bootstrap5_tabs',
    'djangocms_bootstrap5.contrib.bootstrap5_utilities',
    'djangocms_googlemap',
    'djangocms_video',

    'rest_framework',
    'rest_framework_gis',
    "drf_spectacular",
    'rest_framework_datatables_editor',

    'solo',
    'import_export',
    'simple_history',
    'django_extensions',
    'djgeojson',
    'widget_tweaks',
    'taggit',
    'taggit_autosuggest',
    'django_filters',
    'storages',
    'crispy_forms',
    'crispy_bootstrap5',
    'fluent_comments',
    'threadedcomments',
    'django_comments',

    'django_social_share',
    # 'background_task',
    'meta',
    "sortedm2m",
    'ordered_model',
    "rosetta",
    'bootstrap_datepicker_plus',
    "django_gravatar",
    "django_ckeditor_5",
    "django_jsonforms",
    "treewidget",
    'django_htmx',
    'formtools',
    'well_logs',

    # MY APPS
    'main',
    'database',
    'thermal_data',
    'publications', 
    'crossref', 
    'crossref.cms', 
    'mapping',
    'dashboard',
    'data_editor',
    'editorial',
    'review',
    'django_datacite',
    'earth_science',
    "global_tectonics",
    "research_organizations",

    "debug_toolbar",
]

EARTH_MATERIALS_INCLUDE = [
    'Igneous rock and sediment',
    'Metamorphic rock',
    'Sediment and sedimentary rock'
    ]

GRAPPELLI_INDEX_DASHBOARD = 'main.admin_dashboard.AdminDashboard'
GRAPPELLI_AUTOCOMPLETE_LIMIT = None
GRAPPELLI_ADMIN_TITLE = f'{SITE_NAME} Administration'

TREEWIDGET_SETTINGS = {
                'search':True,
                # 'show_buttons': True
                "can_add_related": False,
                }

TREEWIDGET_TREEOPTIONS = {
        "core" : {
            "themes" : {
                "variant" : "large",
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
        "plugins" : [ "checkbox" ]
}

DATACITE_DEFAULTS = {
    # These are default field values. The user cannot change these and they are hidden from the form.
    'resourceTypeGeneral': 'Dataset',
    'publisher': "GFZ Data Services",
}

DATACITE_RECOMMENDED = {
    # These are recommended field values. The user is still able to change these when filling out the form.
    'language': 'en',
    'license': 'CC BY 4.0',
}


ROOT_URLCONF = f'{APP_NAME}.urls'
WSGI_APPLICATION = f'{APP_NAME}.wsgi.application'

META_SITE_NAME = SITE_NAME

DEFAULT_FROM_EMAIL = f'info{EMAIL_DOMAIN}'

TAGGIT_CASE_INSENSITIVE = True

SOCIALACCOUNT_PROVIDERS = {
    'orcid': {
        # Base domain of the API. Default value: 'orcid.org', for the production API
        'BASE_DOMAIN':'sandbox.orcid.org',  # for the sandbox API
        # Member API or Public API? Default: False (for the public API)
        'MEMBER_API': False,
    }
}


# ADAPTER FOR DJANGO-INVITATION TO USE DJANGO-ALLAUTH
ACCOUNT_ADAPTER = 'invitations.models.InvitationsAdapter'


# DJANGO-ORGANISATIONS SETTINGS
INVITATION_BACKEND = 'organizations.backends.defaults.InvitationBackend'
REGISTRATION_BACKEND = 'organizations.backends.defaults.RegistrationBackend'


TEMPLATES[0]['DIRS'].append(os.path.join(APP_NAME, 'templates'))

CROSSREF_UA_STRING = f"{SITE_NAME} (https://thermoglobe.app)"
CROSSREF_MAILTO = ','.join([v[1] for v in ADMINS])

MIDDLEWARE += [
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    "django_htmx.middleware.HtmxMiddleware",
]
# MIDDLEWARE.append('lockdown.middleware.LockdownMiddleware')

# THUMBNAIL_DEFAULT_STORAGE = f'{APP_NAME}.storage_backends.PublicMediaStorage'
# PRIVATE_FILE_STORAGE = DEFAULT_FILE_STORAGE = f'{APP_NAME}.storage_backends.PrivateMediaStorage'

REST_FRAMEWORK = {
    "HTML_SELECT_CUTOFF": 10,
    'DEFAULT_AUTHENTICATION_CLASSES': [ 
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'api.v1.throttling.AnonBurstRate',
        'api.v1.throttling.AnonSustainedRate',
        'api.v1.throttling.UserBurstRate'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon_burst': '4/second',
        'anon_sustained': '30/minute',
        'user_burst': '25/second'
    },
    'DEFAULT_PERMISSION_CLASSES': [
        "api.access_policies.SiteAccessPolicy",
    ],
    'DEFAULT_RENDERER_CLASSES': [
        "drf_orjson_renderer.renderers.ORJSONRenderer",
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_csv.renderers.PaginatedCSVRenderer',
        'drf_excel.renderers.XLSXRenderer',
        'rest_framework_datatables_editor.renderers.DatatablesRenderer',
        'api.v1.renderers.GeoJsonRenderer',
    ],
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework_datatables_editor.filters.DatatablesFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables_editor.pagination.DatatablesPageNumberPagination',

    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
    
    'DEFAULT_PARSER_CLASSES': [
        'drf_orjson_renderer.parsers.ORJSONParser',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}


if os.getenv('DJANGO_ENV') == 'development':

    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

    if os.name == 'nt':
        import platform
        OSGEO4W = r"C:\OSGeo4W"
        # GDAL_LIBRARY_PATH = os.path.join(OSGEO4W, "bin","gdal305.dll")

        # if '64' in platform.architecture()[0]:
            # OSGEO4W += "64"
        assert os.path.isdir(OSGEO4W), "Directory does not exist: " + OSGEO4W
        os.environ['OSGEO4W_ROOT'] = OSGEO4W
        os.environ['GDAL_DATA'] = OSGEO4W + r"\share\gdal"
        os.environ['PROJ_LIB'] = OSGEO4W + r"\share\proj"
        os.environ['PATH'] = OSGEO4W + r"\bin;" + os.environ['PATH']

    DATABASES = {
        'default': {
            'CONN_MAX_AGE': 0,
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USERNAME'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': 'localhost',
            'ENGINE':'django.contrib.gis.db.backends.postgis',
            }
        }


else:
    import django_heroku, dj_database_url  
    STATICFILES_STORAGE = f'{APP_NAME}.storage_backends.StaticStorage'
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_STATIC_LOCATION}/"

    SECURE_SSL_REDIRECT = True
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600, 
            ssl_require=True)
    }
    django_heroku.settings(locals(), staticfiles=False)
    DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'
