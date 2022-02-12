import django_heroku, dj_database_url  

SECURE_SSL_REDIRECT = True

DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600, 
        ssl_require=True)
}

#KEEP THIS LAST
django_heroku.settings(locals(), staticfiles=False)