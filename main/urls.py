from django.urls import path
from main.views import HomeView, FieldDescriptionsView, NewsView, FAQView, LandingPage
app_name = 'main'

urlpatterns = [
    path('', LandingPage.as_view(),name='landing'),
    path('about/', HomeView.as_view(),name='home'),
    path('field-descriptions', FieldDescriptionsView.as_view(),name='field_descriptions'),
    path('news/', NewsView.as_view(), name='news'),
    path('frequently-asked-questions/', FAQView.as_view(), name='faqs'),
]
