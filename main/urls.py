from django.urls import path
from main import views
app_name = 'main'

urlpatterns = [
    path('', views.LandingPage.as_view(),name='landing'),
    path('about/', views.HomeView.as_view(),name='home'),
    path('field-descriptions', views.FieldDescriptionsView.as_view(),name='field_descriptions'),
    path('news/', views.NewsView.as_view(), name='news'),
    path('frequently-asked-questions/', views.FAQView.as_view(), name='faqs'),
]
