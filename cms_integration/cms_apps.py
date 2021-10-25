from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.urls import path, include
from thermoglobe import views

@apphook_pool.register  # register the application
class WorldMap(CMSApp):
    app_name = "thermoglobe"
    name = "World Map"

    def get_urls(self, page=None, language=None, **kwargs):
        return [
            path('',views.WorldMap.as_view(),name='world_map'),
        ]

@apphook_pool.register  # register the application
class Publications(CMSApp):
    app_name = "publications"
    name = "Publications"

    def get_urls(self, page=None, language=None, **kwargs):
        return ["publications.urls"]
