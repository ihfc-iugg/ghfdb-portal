import os
import platform
from django.utils.translation import ugettext_lazy as _

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


ALLOWED_HOSTS = ['161.35.100.229','heatflow.org','www.heatflow.org','localhost']


# CHANGE FOR PRODUCTION
DEBUG = os.environ['DEBUG'],
RECAPTCHA_PUBLIC_KEY = os.environ['RECAPTCHA_PUBLIC_KEY']
RECAPTCHA_PRIVATE_KEY = os.environ['RECAPTCHA_PRIVATE_KEY']
SECRET_KEY = os.environ['SECRET_KEY']


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILTERS_EMPTY_CHOICE_LABEL = None

# Application definition
INSTALLED_APPS = [
    # 'django.forms',
    'djangocms_admin_style',  # for the admin skin.
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django.contrib.humanize',
    'django.contrib.admindocs',
    'users',
    'sekizai',
    'main',
    'mapping',
    'thermoglobe',
    # 'tables',
    'sortedm2m',
    'import_export',
    # 'debug_toolbar',
    'simple_history',
    'captcha',
    'betterforms',
    'django_extensions',
    # 'django_filters',
    'djgeojson',
    'widget_tweaks',
    'ckeditor',
    'meta',
    'django_cleanup.apps.CleanupConfig',
]

MIDDLEWARE = [
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

INTERNAL_IPS = [
    # ...
    '127.0.0.1',
    # ...
]

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USERNAME'],
        'PASSWORD': os.environ['DB_PASSWORD'],
    },
} 

ROOT_URLCONF = 'heatflow.urls'

# FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'sekizai.context_processors.sekizai',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                "django.template.context_processors.i18n",
            ],
        },
    },
]

WSGI_APPLICATION = 'heatflow.wsgi.application'


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization

LANGUAGES = (
    ('en', _('English')),
    ('fr', _('French')),
    ('pl', _('Polish')),
)

LANGUAGE_CODE = 'en'
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale/'),
)


TIME_ZONE = 'Australia/Adelaide'

USE_I18N = True

USE_L10N = True

USE_TZ = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'file_cache': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'cache','file'),
        'TIMEOUT': 86400,
        'OPTIONS': {
            'MAX_ENTRIES': 100
        }
    },
    'plots': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'cache','plots'),
        'TIMEOUT': None,
        'OPTIONS': {
            'MAX_ENTRIES': 100
        }
    }
}


SERIALIZATION_MODULES = {
    "geojson": "django.contrib.gis.serializers.geojson", 
 }

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/assets/'
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR, 'assets')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_DIRS = []

META_SITE_PROTOCOL = 'https'
META_SITE_DOMAIN = 'heatflow.org'
META_INCLUDE_KEYWORDS = ['heat flow','thermoglobe','heat flow','temperature','thermal','earth','science','research']
META_DEFAULT_KEYWORDS = ['heat flow','thermoglobe','heat flow','temperature','thermal','earth','science','research']
META_USE_TITLE_TAG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

AUTH_USER_MODEL = 'users.CustomUser' # new

IMPORT_EXPORT_SKIP_ADMIN_LOG = True

CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono',
        # 'skin': 'office2013',
        'toolbar_Basic': [
            ['Source', '-', 'Bold', 'Italic']
        ],
        'toolbar_YourCustomToolbarConfig': [
            {'name': 'document', 'items': ['Source', '-', 'Maximize', 'Save', 'NewPage', 'Preview', 'Print', '-', 'Templates']},
            {'name': 'clipboard', 'items': ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
            {'name': 'editing', 'items': ['Find', 'Replace',]},
            {'name': 'links', 'items': ['CreateDiv','Link', 'Unlink', 'Anchor']},
            {'name': 'insert',
             'items': ['Image', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar',]},
            '/',

            {'name': 'basicstyles',
             'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript',]},
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock',]},
            {'name': 'styles', 'items': ['Styles', 'Format',]},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},

        ],
        'toolbar': 'YourCustomToolbarConfig',  # put selected toolbar config here
        # 'toolbarGroups': [{ 'name': 'document', 'groups': [ 'mode', 'document', 'doctools' ] }],
        'height': 900,
        'width': '100%',
        # 'toolbarCanCollapse': True,
        'tabSpaces': 4,
        'extraPlugins': ','.join([
            'uploadimage', # the upload image feature
            # your extra plugins here
            'div',
            'autolink',
            'autoembed',
            'embedsemantic',
            'autogrow',
            # 'devtools',
            'widget',
            'lineutils',
            'clipboard',
            'dialog',
            'dialogui',
            'elementspath'
        ]),
        'stylesSet': [
            {
                "name": 'Banner',
                "element": 'section',
                "attributes": {'class': 'banner'},
            }, {
                "name": 'Section',
                "element": 'section',
            }, {
                "name": 'Header',
                "element": 'header',
                "attributes": {'class': 'major'},
            }, {
                "name": 'Code',
                "element": 'code',
            }, {
                "name": 'Footnote',
                "element": 'p',
                "attributes": {'class': 'footnote'},
            },            
        ],
    }
}
