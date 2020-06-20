from django.urls import path, include
from thermoglobe import views
app_name = 'thermoglobe'

urlpatterns = [
    path('thermoglobe/', 
        include([
            path('',views.About.as_view(), name='about'),
            path('sites/<slug>/', views.SiteView.as_view(), name='site'),
            path('upload/',views.UploadView.as_view(),name='upload'),
        ])),
]
    