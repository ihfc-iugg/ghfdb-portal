from django.urls import path
from user.views import user_settings

app_name = 'user'
urlpatterns = [
    path('settings/', user_settings, name='settings'),
]
