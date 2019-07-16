from django.urls import path
from main import views
app_name = 'main'

urlpatterns = [
    path('',views.HomeView.as_view(),name='home'),
    path('resources/',views.resources,name='resources'),
    path('about/',views.AboutView.as_view(),name='about'),
    path('contact/',views.ContactView.as_view(),name='contact'),
    path('thermoglobe/',views.DatabaseView.as_view(),name='database'),
    path('thermoglobe/site/<site_id>/<site_name>/', views.SiteView.as_view(), name='site'),
    path('upload/',views.UploadView.as_view(),name='upload'),
    path('upload/confirm/',views.ConfirmUploadView.as_view(),name='confirm_upload'),
    path('thermoglobe/filter', views.filter_data,name='filter_data')
    # path('confirm/',confirm,name='confirm'),
]
