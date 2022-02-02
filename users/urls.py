from django.urls import path
from users.views import why_register

app_name = 'users'
urlpatterns = [
    path('why-register/', why_register, name='why_register'),
]
