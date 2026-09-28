"""Settings that apply only when ``DJANGO_ENV=production``."""

from botocore.config import Config

# Required for the switch to the GFZ dog service.
AWS_STORAGE_BUCKET_NAME = "dog-ext.heatflow-world.ghfdb"
AWS_S3_ENDPOINT_URL = "https://s3.gfz-potsdam.de"
AWS_S3_CLIENT_CONFIG = Config(
    request_checksum_calculation="when_required",
    response_checksum_validation="when_required",
)
