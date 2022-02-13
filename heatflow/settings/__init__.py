from split_settings.tools import include
from os import environ
from comments.app_settings import *
from authentication.app_settings import *
import os 

APP_NAME = 'heatflow'

DEBUG = True if environ.get('DEBUG') == 'TRUE' else False

include(*[
    'components/*.py',
    f"environments/{environ.get('DJANGO_ENV','development')}.py",
])

ALLOWED_HOSTS = ['127.0.0.1','localhost','thermoglobe.herokuapp.com','www.thermoglobe.app','thermoglobe.app']


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

    'import_export',
    'simple_history',
    'django_extensions',
    'djgeojson',
    'widget_tweaks',
    'taggit',
    'taggit_autosuggest',
    'django_filters',
    # 'storages',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_comments_xtd',
    'django_comments',
    'django_social_share',
    'background_task',
    'lockdown',
    'meta',
    "sortedm2m",
    'ordered_model',
    "rosetta",
    
    # MY APPS
    'thermoglobe',
    'publications', 
    'mapping',
    'dashboard',
    'data_editor',
    'editorial',
    'comments',

    # "debug_toolbar",
]

CRISPY_ALLOWED_TEMPLATE_PACKS = CRISPY_TEMPLATE_PACK = "bootstrap5"

GRAPPELLI_ADMIN_TITLE='ThermoGlobe'

ADMINS = MANAGERS = [('Sam','admin@thermoglobe.app')]
DEFAULT_FROM_EMAIL = 'admin@thermoglobe.app'
COMMENTS_XTD_FROM_EMAIL = "messaging@thermoglobe.app"
COMMENTS_XTD_CONTACT_EMAIL = "info@thermoglobe.app"

META_SITE_DOMAIN = 'thermoglobe.app'
META_SITE_NAME = 'ThermoGlobe'
META_INCLUDE_KEYWORDS = ['heat flow','thermoglobe','temperature','geothermal','earth','science','research','data']
META_DEFAULT_KEYWORDS = ['heat flow','thermoglobe','temperature','geothermal','earth','science','research','data']


TAGGIT_CASE_INSENSITIVE = True

RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')

SOCIALACCOUNT_PROVIDERS = {
    'orcid': {
        # Base domain of the API. Default value: 'orcid.org', for the production API
        'BASE_DOMAIN':'sandbox.orcid.org',  # for the sandbox API
        # Member API or Public API? Default: False (for the public API)
        'MEMBER_API': False,
    }
}

