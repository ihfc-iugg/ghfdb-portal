from django.test import SimpleTestCase
from django.urls import reverse, resolve
from main.views import WorldMap, SiteView


class TestUrls(SimpleTestCase):

    def test_world_map_resolves(self):
        url = reverse('main:world_map')
        self.assertEquals(resolve(url).func.__name__, WorldMap.as_view().__name__)

    # def test_site_detail_is_resolved(self):
        # url = reverse('main:site')
        # self.assertEquals(resolve(url).func, SiteView.as_view())
        # self.assertIsInstance(resolve(url).func, SiteView)

        