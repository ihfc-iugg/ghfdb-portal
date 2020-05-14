from django.urls import path, include
from thermoglobe import views
app_name = 'thermoglobe'

urlpatterns = [

    path('thermoglobe/', 
        include([
            path('',views.About.as_view(), name='about_thermoglobe'),
            path('sites/<slug>/', views.SiteView.as_view(), name='site'),
            path('upload/',views.UploadView.as_view(),name='upload'),
        ])),



    # path('thermoglobe/', views.About.as_view(), name='about_thermoglobe'),
    # path('thermoglobe/site/<pk>/', views.SiteView.as_view(), name='site'),
    # path('thermoglobe/upload/',views.UploadView.as_view(),name='upload'),
    # path('thermoglobe/upload/confirm/',views.ConfirmUploadView.as_view(),name='confirm_upload'),
    # path('resources/charts',views.chart_resources,name='charts'),

]
    