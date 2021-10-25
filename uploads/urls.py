from django.urls import path
from thermoglobe import views

urlpatterns = [
    path('upload/',views.UploadView.as_view(),name='upload'),
    path('upload/confirm', views.upload_confirm, name='confirm_upload'),
    path('upload_template/<template_name>', views.get_upload_template, name='template'),
]