from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage, S3StaticStorage

class StaticStorage(S3StaticStorage):
    location = settings.AWS_STATIC_LOCATION
    default_acl="public-read"

class PublicMediaStorage(S3Boto3Storage):
    location = settings.AWS_PUBLIC_MEDIA_LOCATION
    file_overwrite = False
    default_acl="public-read"

class PrivateMediaStorage(S3Boto3Storage):
    location = settings.AWS_PRIVATE_MEDIA_LOCATION
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False