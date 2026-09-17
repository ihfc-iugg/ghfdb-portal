"""Factory-boy factories for the review app's test suite (T002).

A publication is supplied directly by ``fairdm.factories.LiteratureItemFactory``
— nothing here redefines it.
"""

import factory
from fairdm.factories import DatasetFactory, LiteratureItemFactory, PersonFactory
from review.models import Review


class ClaimedPersonFactory(PersonFactory):
    """A person who has claimed their profile: a usable password and
    ``is_claimed=True``, unlike ``PersonFactory``'s own unclaimed default."""

    is_claimed = True
    password = factory.PostGenerationMethodCall("set_password", "test-pass-123")


class GhostPersonFactory(PersonFactory):
    """An unclaimed profile with no email — added for attribution alone,
    the same shape an assessor named on the form but never signed up gets."""

    email = None
    is_claimed = False


class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Review

    literature = factory.SubFactory(LiteratureItemFactory)
    dataset = factory.SubFactory(DatasetFactory)
