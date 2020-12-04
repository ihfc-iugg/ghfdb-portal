from django.test import TestCase

# # Create your tests here.
from model_bakery import baker


class SiteTestModel(TestCase):
    """
    Class to test the model Customer
    """

    def setUp(self):
        self.site = baker.make('thermoglobe.Site')