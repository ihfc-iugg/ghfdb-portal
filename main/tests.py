from django.test import TestCase
from .models import Site

# Create your tests here.
class SiteTestCase(TestCase):
    def setUp(self):
        test_site = {
            'site_name':'test_site',
            'latitude': -35.75849,
            'longitude': 137.2378,
            'elevation': 350,
            'well_depth': 1500,
            'operator': 'arsenal_fc',
            'cruise': 'im-a-cruise',
        }

        Site.objects.create(**test_site)

    def test_geom_is_saved(self):
        site = Site.objects.get(site_name='test_site')
        self.assertEqual(site.geom.x, site.longitude)
        self.assertEqual(site.geom.y, site.latitude)

    # def test_min_latitude(self):
    #     site = Site.objects.get(site_name='test_site')
    #     site.latitude = -120
    #     site.save()
    #     self.assertFalse(site.latitude == -120)