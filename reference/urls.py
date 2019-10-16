from django.urls import path
from . import views
app_name = 'reference'

urlpatterns = [

    path('thermoglobe/publications/',views.AllReferencesView.as_view(),name='reference_list'),
    path('thermoglobe/publications/<pk>/',views.ReferenceView.as_view(),name='reference_details'),]
