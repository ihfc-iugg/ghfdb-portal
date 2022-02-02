
import os, django_heroku, dj_database_url 
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

# ALLOWED_HOSTS = ['161.35.100.229','heatflow.org','www.heatflow.org','localhost']
ALLOWED_HOSTS = ['localhost','thermoglobe.herokuapp.com','www.heatflow.org','heatflow.org']

# CHANGE FOR PRODUCTION
DEBUG = True if os.environ.get('DEBUG') == 'TRUE' else False

SECRET_KEY = os.environ.get('SECRET_KEY')

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SITE_ID = 1

DATA_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILTERS_EMPTY_CHOICE_LABEL = None

LOGIN_REDIRECT_URL = '/dashboard/'
LOGIN_URL = '/accounts/login/'

# Application definition
INSTALLED_APPS = [
    'grappelli',
    # 'djangocms_admin_style',  # for the admin skin.
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'django_cleanup.apps.CleanupConfig',
    'users',
    'django.contrib.gis',
    'django.contrib.humanize',
    'django.contrib.admindocs',
    "allauth", # new
    "allauth.account", # new
    "allauth.socialaccount", # new
    "allauth.socialaccount.providers.google",
    # "allauth.socialaccount.providers.github",
    "allauth.socialaccount.providers.orcid",
    "allauth.socialaccount.providers.openid",
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
    'djangocms_style',
    'rest_framework',
    'rest_framework_gis',
    'rest_framework_datatables_editor',
    'mapping',
    'thermoglobe',
    'dashboard',
    'import_export',
    # 'simple_history',
    'captcha',
    'django_extensions',
    'djgeojson',
    'widget_tweaks',
    'ckeditor',
    'meta',
    # 'djangocms_faq',
    'aldryn_apphooks_config',
    'taggit',
    'taggit_autosuggest',
    # 'djangocms_blog',
    'publications', 
    'data_editor',
    'editorial',
    'ordered_model', 

    'crispy_forms',
    'django_filters',
    'django_comments',
    ]

MIDDLEWARE = [
    'cms.middleware.utils.ApphookReloadMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

INTERNAL_IPS = ['127.0.0.1']

DATABASES = {}

# set to False to use debug in production
if DEBUG:
    DATABASES['default'] = {
        'CONN_MAX_AGE': 0,
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USERNAME'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': 'localhost',
        # 'ENGINE':'django.contrib.gis.db.backends.postgis',
    }
else:
    DATABASES['default'] = dj_database_url.config()


ROOT_URLCONF = 'heatflow.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'heatflow', 'templates'),
        ],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.template.context_processors.csrf',
                'django.template.context_processors.tz',
                'sekizai.context_processors.sekizai',
                'django.template.context_processors.static',
                'cms.context_processors.cms_settings'
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader'
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


LANGUAGES = (
    ('en', _('English')),
    ('fr', _('French')),
    ('de', _('German')),
)

CMS_LANGUAGES = {
    ## Customize this
    1: [
        {
            'code': 'en',
            'name': _('en'),
            'redirect_on_fallback': True,
            'public': True,
            'hide_untranslated': False,
        },
    ],
    'default': {
        'redirect_on_fallback': True,
        'public': True,
        'hide_untranslated': False,
    },
}

CMS_TEMPLATES = (
    ## Customize this
    ('fullwidth.html', 'Fullwidth'),
    # ('sidebar_left.html', 'Sidebar Left'),
    # ('sidebar_right.html', 'Sidebar Right')
)

X_FRAME_OPTIONS = 'SAMEORIGIN'

CMS_PERMISSION = True

CMS_PLACEHOLDER_CONF = {}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale/'),
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
}

SERIALIZATION_MODULES = {
    "geojson": "django.contrib.gis.serializers.geojson", 
 }

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# STATICFILES_DIRS = (
#     os.path.join(BASE_DIR, 'static'),
# )


META_SITE_PROTOCOL = 'https'
META_SITE_DOMAIN = 'heatflow.org'
META_SITE_NAME = 'HeatFlow.org'
META_INCLUDE_KEYWORDS = ['heat flow','thermoglobe','heat flow','temperature','thermal','earth','science','research']
META_DEFAULT_KEYWORDS = ['heat flow','thermoglobe','heat flow','temperature','thermal','earth','science','research']
META_USE_TITLE_TAG = True
META_USE_SITES = True
META_USE_OG_PROPERTIES = True
META_USE_TWITTER_PROPERTIES = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
AUTH_USER_MODEL = 'users.CustomUser'

IMPORT_EXPORT_SKIP_ADMIN_LOG = True

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters'
)

THUMBNAIL_HIGH_RESOLUTION = True

# django-taggit
TAGGIT_CASE_INSENSITIVE = True

RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')


# Rest Framework
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

# DJANGO-ALLAUTH
ACCOUNT_LOGOUT_ON_GET = True #skip confirm logout screen
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True 
ACCOUNT_USERNAME_REQUIRED = False #using email os this is False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_EMAIL_VERIFICATION = 'mandatory' #email verification is REQUIRED
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True #log new user in after confirming email
AUTHENTICATION_BACKENDS = (
    "allauth.account.auth_backends.AuthenticationBackend",
)

SOCIALACCOUNT_PROVIDERS = {
    # 'openid': {
    #     'SERVERS': [
    #         dict(id='yahoo',
    #              name='Yahoo',
    #              openid_url='http://me.yahoo.com'),
    #         dict(id='hyves',
    #              name='Hyves',
    #              openid_url='http://hyves.nl'),
    #         dict(id='google',
    #              name='Google',
    #              openid_url='https://www.google.com/accounts/o8/id'),
    #     ]
    # },
    'google': {
        'SCOPE': [
            'profile',
            'openid',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    },
    'orcid': {
        # Base domain of the API. Default value: 'orcid.org', for the production API
        'BASE_DOMAIN':'sandbox.orcid.org',  # for the sandbox API
        # Member API or Public API? Default: False (for the public API)
        'MEMBER_API': False,
    }
}

ACCOUNT_FORMS = {
    'change_password': 'allauth.account.forms.ChangePasswordForm',
    'disconnect': 'allauth.socialaccount.forms.DisconnectForm',
    'login': 'users.forms.CustomLoginForm',
    'reset_password': 'allauth.account.forms.ResetPasswordForm',
    'reset_password_from_key': 'allauth.account.forms.ResetPasswordKeyForm',
    'set_password': 'allauth.account.forms.SetPasswordForm',
    'signup': 'users.forms.SignUpForm',
        }

SOCIALACCOUNT_FORMS = {
    'disconnect': 'allauth.socialaccount.forms.DisconnectForm',
    'signup': 'users.forms.SocialSignupForm',
}

# For error logging in production
ADMINS = MANAGERS = [('Sam','debugger@geoluminate.com.au')]


# Coloured Messages
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
        messages.DEBUG: 'alert-secondary',
        messages.INFO: 'alert-info',
        messages.SUCCESS: 'alert-success',
        messages.WARNING: 'alert-warning',
        messages.ERROR: 'alert-danger',
 }


# GRAPELLI ADMIN CUSTOMIZATION
GRAPPELLI_ADMIN_TITLE='The Mbantua Collection Administration'
GRAPPELLI_SWITCH_USER=True


django_heroku.settings(locals(), staticfiles=False)
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'