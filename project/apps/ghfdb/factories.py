# import tzinfo from datetime
import datetime
from datetime import tzinfo

import factory
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from faker.providers import BaseProvider
from geoluminate.contrib.controlled_vocabulary.models import ControlledVocabulary
from geoluminate.models import Geoluminate

from .models import HeatFlow, Interval


class VocabularyIterator(factory.Iterator):
    def __init__(self, label, *args, **kwargs):
        iterator = ControlledVocabulary.objects.get(label=label).get_descendants()
        super().__init__(iterator, *args, **kwargs)


class GeoDjangoPointProvider(BaseProvider):
    def geo_point(self, **kwargs):
        faker = factory.faker.faker.Faker()
        coords = faker.latlng(**kwargs)
        return Point(x=float(coords[1]), y=float(coords[0]), srid=4326)


factory.Faker.add_provider(GeoDjangoPointProvider)


class UserFactory(factory.Factory):
    class Meta:
        model = get_user_model()

    email = factory.LazyAttribute(lambda o: f"{o.first_name}.{o.last_name}@fakemail.org")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")


class GeoluminateFactory(factory.Factory):
    class Meta:
        model = Geoluminate

    name = factory.Faker("name")
    acquired = factory.Faker("date_time")
    comment = factory.Faker("text")
    elevation = factory.Faker("pyint", min_value=0, max_value=10000)
    geom = factory.Faker("geo_point")


class HeatFlowFactory(GeoluminateFactory):
    class Meta:
        model = HeatFlow

    q = factory.Faker("pyfloat", min_value=-(10**6), max_value=10**6)
    q_unc = factory.Faker("pyfloat", min_value=0, max_value=10**6)
    q_date_acq = factory.Faker("date_time", tzinfo=datetime.timezone.utc)
    borehole_depth = factory.Faker("pyfloat", min_value=0, max_value=15000)
    expedition = factory.Faker("name")
    # environment = VocabularyIterator("environment")
    water_temp = factory.Faker("pyfloat", min_value=-20, max_value=10000)
    # explo_method = VocabularyIterator("explo_method")
    # explo_purpose = VocabularyIterator("explo_purpose")


class IntervalFactory(factory.Factory):
    class Meta:
        model = Interval

    qc = factory.Faker("pyfloat", min_value=-(10**6), max_value=10**6)
    qc_unc = factory.Faker("pyfloat", min_value=0, max_value=10**6)
    q_method = VocabularyIterator("explo_method")
    q_top = factory.Faker("pyfloat", min_value=0, max_value=10000)
    q_bot = factory.Faker("pyfloat", min_value=0, max_value=10000)
    hf_pen = factory.Faker("pyfloat", min_value=0, max_value=100)
    hf_probe = VocabularyIterator("hf_probe")
    hf_probeL = factory.Faker("pyfloat", min_value=0, max_value=100)
    probe_tilt = factory.Faker("pyfloat", min_value=0, max_value=90)
    q_tf_mech = VocabularyIterator("q_tf_mech")
    q_date_acq = factory.Faker("date_time", tzinfo=datetime.timezone.utc)

    tc_mean = factory.Faker("pyfloat", min_value=0, max_value=100)
    tc_uncertainty = factory.Faker("pyfloat", min_value=0, max_value=100)
    tc_source = VocabularyIterator("tc_source")
    tc_method = factory.Faker("text")
    tc_saturation = factory.Faker("text")
    tc_pT_conditions = VocabularyIterator("tc_pT_conditions")
    tc_pT_function = factory.Faker("text")
    tc_strategy = factory.Faker("text")
    tc_uncertainty = factory.Faker("pyint", min_value=1, max_value=100)

    # correction = factory.Faker("pyfloat", min_value=0, max_value=100)
