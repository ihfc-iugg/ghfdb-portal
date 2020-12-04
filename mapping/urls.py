from django.urls import path, include
from . import views
app_name = 'mapping'

urlpatterns = [
    path('', 
        include([
            path('<model>/<slug>', views.DescribeField.as_view(), name='describe_field'),
            path('<model>/', views.Describe.as_view(), name='describe'),
        ])),
]


