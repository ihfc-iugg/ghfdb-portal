import os
from core.settings import *
from django.utils.translation import ugettext_lazy as _
import djangocms_faq
SITE_NAME = 'ThermoGlobe'
EMAIL_DOMAIN = "@thermoglobe.app"
APP_NAME = 'heatflow'
ADMINS = MANAGERS = [('Sam','sam.jennings@geoluminate.com.au')]

# UNCOMMENT TO COLLECTSTATIC TO AWS S3
# STATICFILES_STORAGE = f'{APP_NAME}.storage_backends.StaticStorage'
# STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_STATIC_LOCATION}/"


ALLOWED_HOSTS += ['thermoglobe.herokuapp.com','www.thermoglobe.app','thermoglobe.app']

INSTALLED_APPS = [
    'core',
    'grappelli',
    'django.contrib.auth',
    'django.contrib.contenttypes',
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
    'djangocms_googlemap',
    'djangocms_video',

    'rest_framework',
    'rest_framework_gis',
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
    'django_comments_xtd',
    'django_comments',
    'django_social_share',
    'background_task',
    'meta',
    "sortedm2m",
    'ordered_model',
    "rosetta",

    # MY APPS
    'thermoglobe',
    'well_logs',
    'crossref', 
    'crossref.cms', 
    'publications', 
    'mapping',
    'dashboard',
    'data_editor',
    'editorial',
    # 'comments',

    # "debug_toolbar",
]

ROOT_URLCONF = f'{APP_NAME}.urls'
WSGI_APPLICATION = f'{APP_NAME}.wsgi.application'

GRAPPELLI_ADMIN_TITLE = f'{SITE_NAME} Administration'
META_SITE_NAME = SITE_NAME
COMMENTS_XTD_FROM_EMAIL = f"noreply{EMAIL_DOMAIN}"
COMMENTS_XTD_CONTACT_EMAIL = f"info{EMAIL_DOMAIN}"
DEFAULT_FROM_EMAIL = f'info{EMAIL_DOMAIN}'

TAGGIT_CASE_INSENSITIVE = True

RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY')



SOCIALACCOUNT_PROVIDERS = {
    'orcid': {
        # Base domain of the API. Default value: 'orcid.org', for the production API
        'BASE_DOMAIN':'sandbox.orcid.org',  # for the sandbox API
        # Member API or Public API? Default: False (for the public API)
        'MEMBER_API': False,
    }
}

TEMPLATES[0]['DIRS'].append(os.path.join(APP_NAME, 'templates'))

CROSSREF_UA_STRING = "ThermoGlobe Research Database (https://thermoglobe.app)"
CROSSREF_MAILTO = 'sam.jennings@geoluminate.com.au'
CROSSREF_MODELS = {
    'publication': 'publications.Publication',
    'author': 'publications.Author'
}
CROSSREF_DEFAULT_STYLE = 'harvard'
CROSSREF_AUTHOR_TRUNCATE_AFTER = 2


CROSSREF_CMS_STYLES = [
            ('harvard', 'Harvard'),
        ]

# MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
# MIDDLEWARE.append('lockdown.middleware.LockdownMiddleware')


THUMBNAIL_DEFAULT_STORAGE = f'{APP_NAME}.storage_backends.PublicMediaStorage'
PRIVATE_FILE_STORAGE = DEFAULT_FILE_STORAGE = f'{APP_NAME}.storage_backends.PrivateMediaStorage'


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
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        # 'api.v1.renderers.UJSONRenderer',
        # 'rest_framework.renderers.JSONRenderer',
        "drf_orjson_renderer.renderers.ORJSONRenderer",
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_csv.renderers.PaginatedCSVRenderer',
        'drf_excel.renderers.XLSXRenderer',
        'rest_framework_datatables_editor.renderers.DatatablesRenderer',
    ],

    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework_datatables_editor.filters.DatatablesFilterBackend',
    ),

    'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables_editor.pagination.DatatablesPageNumberPagination',

    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
    
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],

}

LANGUAGES = (
    ## Customize this
    ('en', _('English')),
    ('de', _('German')),
    ('fr', _('French')),
    ('it', _('Italian')),
)


if os.getenv('DJANGO_ENV') == 'development':
    if os.name == 'nt':
        import platform
        OSGEO4W = r"C:\OSGeo4W"
        if '64' in platform.architecture()[0]:
            OSGEO4W += "64"
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
