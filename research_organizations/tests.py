from django.test import TestCase
from .models import ResearchOrganization as RO

data = """   {
      "id": "https://ror.org/04z8jg394",
      "name": "Helmholtz Centre Potsdam - GFZ German Research Centre for Geosciences",
      "email_address": "",
      "ip_addresses": [],
      "established": 1992,
      "types": [
        "Facility"
      ],
      "relationships": [
        {
          "label": "Helmholtz Association of German Research Centres",
          "type": "Parent",
          "id": "https://ror.org/0281dp749"
        }
      ],
      "addresses": [
        {
          "lat": 52.382556,
          "lng": 13.064444,
          "state": "Brandenburg",
          "state_code": "DE-BB",
          "city": "Potsdam",
          "geonames_city": {
            "id": 2852458,
            "city": "Potsdam",
            "geonames_admin1": {
              "name": "Brandenburg",
              "id": 2945356,
              "ascii_name": "Brandenburg",
              "code": "DE.11"
            },
            "geonames_admin2": {
              "name": null,
              "id": null,
              "ascii_name": null,
              "code": null
            },
            "license": {
              "attribution": "Data from geonames.org under a CC-BY 3.0 license",
              "license": "http://creativecommons.org/licenses/by/3.0/"
            },
            "nuts_level1": {
              "name": "BRANDENBURG",
              "code": "DE4"
            },
            "nuts_level2": {
              "name": "Brandenburg",
              "code": "DE40"
            },
            "nuts_level3": {
              "name": "Potsdam-Mittelmark",
              "code": "DE40E"
            }
          },
          "postcode": null,
          "primary": false,
          "line": null,
          "country_geonames_id": 2921044
        }
      ],
      "links": [
        "http://www.gfz-potsdam.de/en/home/"
      ],
      "aliases": [],
      "acronyms": [
        "GFZ"
      ],
      "status": "active",
      "wikipedia_url": "https://en.wikipedia.org/wiki/GFZ_German_Research_Centre_for_Geosciences",
      "labels": [
        {
          "label": "Helmholtz-Zentrum Potsdam - Deutsches GeoForschungsZentrum GFZ",
          "iso639": "de"
        }
      ],
      "country": {
        "country_name": "Germany",
        "country_code": "DE"
      },
      "external_ids": {
        "ISNI": {
          "preferred": null,
          "all": [
            "0000 0000 9195 2461"
          ]
        },
        "Wikidata": {
          "preferred": null,
          "all": [
            "Q1205654"
          ]
        },
        "GRID": {
          "preferred": "grid.23731.34",
          "all": "grid.23731.34"
        }
      }
    }"""

# class AnimalTestCase(TestCase):

#     def setUp(self):
        
#         RO.objects.create(**data)

#     def test_animals_can_speak(self):
#         """Animals that can speak are correctly identified"""
#         lion = RO.objects.get(name="lion")
#         cat = RO.objects.get(name="cat")
#         self.assertEqual(lion.speak(), 'The lion says "roar"')
#         self.assertEqual(cat.speak(), 'The cat says "meow"')