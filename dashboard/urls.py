from django.urls import path
from dashboard.views import dashboard, user_settings

app_name = 'dashboard'
urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('settings/', user_settings, name='settings'),

]
