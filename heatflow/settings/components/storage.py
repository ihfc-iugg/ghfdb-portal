import os
APP_NAME = 'heatflow'

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_S3_REGION_NAME = 'ap-southeast-2'

AWS_DEFAULT_ACL=None
AWS_STATIC_LOCATION = 'static'
STATICFILES_STORAGE = f'{APP_NAME}.storage_backends.StaticStorage'
STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_STATIC_LOCATION}/"

AWS_PUBLIC_MEDIA_LOCATION =  'media/public'
THUMBNAIL_DEFAULT_STORAGE = f'{APP_NAME}.storage_backends.PublicMediaStorage'

AWS_PRIVATE_MEDIA_LOCATION = 'media/private'
PRIVATE_FILE_STORAGE = DEFAULT_FILE_STORAGE = f'{APP_NAME}.storage_backends.PrivateMediaStorage'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
}