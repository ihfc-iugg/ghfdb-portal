from django.urls import path
from main import views
app_name = 'main'

urlpatterns = [
    path('',views.HomeView.as_view(),name='home'),
    path('about/',views.AboutView.as_view(),name='about'),
    path('contact/',views.ContactView.as_view(),name='contact'),
    path('resources/',views.ResourcesView.as_view(),name='resources'),
    path('resources/field_descriptions',views.FieldDescriptionsView.as_view(),name='field_descriptions')
]
