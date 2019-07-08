from django.urls import path
from .views import DatabaseView, UploadView, ConfirmUploadView, SiteView, filter_data
app_name = 'database'

urlpatterns = [

    path('database/',DatabaseView.as_view(),name='database'),
    path('database/site/<int:site_id>/<site_name>/', SiteView.as_view(), name='site'),
    path('upload/',UploadView.as_view(),name='upload'),
    path('upload/confirm/',ConfirmUploadView.as_view(),name='confirm_upload'),
    path('database/a', filter_data,name='filter_data')
    # path('confirm/',confirm,name='confirm'),
]
