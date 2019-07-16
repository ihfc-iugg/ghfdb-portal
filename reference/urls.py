from django.urls import path
from . import views
app_name = 'reference'

urlpatterns = [

    path('references/',views.AllReferencesView.as_view(),name='reference_list'),
    path('references/<reference_id>/<reference_slug>/',views.ReferenceView.as_view(),name='reference_details'),

]
