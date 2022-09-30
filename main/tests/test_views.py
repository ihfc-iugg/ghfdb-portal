from django.test import TestCase, Client
from django.urls import reverse, resolve
from main.views import WorldMap, SiteView
from database.models import Site, Interval
import json

class TestViews(TestCase):


    def test_world_map_GET(self):
        response = self.client.get('/en/')
        # response = self.client.get(reverse('main:world_map'))
        self.assertEquals(response.status_code, 200)
        # self.assertTemplateUsed(response, 'mapping/application.html')


        