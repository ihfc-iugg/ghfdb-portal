import dj_database_url  
import os 

SECURE_SSL_REDIRECT = True

DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600, 
        ssl_require=True)
}


SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'apikey' # this is exactly the value 'apikey'
EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
EMAIL_PORT = 587
EMAIL_USE_TLS = True

