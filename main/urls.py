from django.urls import path
from main.views import HomeView, FieldDescriptionsView, NewsView, FAQView, CitationView, LicenseView
app_name = 'main'

urlpatterns = [
    path('', HomeView.as_view(),name='home'),
    path('field_descriptions', FieldDescriptionsView.as_view(),name='field_descriptions'),
    path('news/', NewsView.as_view(), name='news'),
    path('frequently-asked-questions/', FAQView.as_view(), name='faqs'),
    path('how-to-cite/', CitationView.as_view(), name='citation'),
    path('licensing/', LicenseView.as_view() ,name='license'),
]
