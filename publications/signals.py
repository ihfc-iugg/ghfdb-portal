from .models import Publication, Author
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .widgets import get_author_objects


# # signals.py
# @receiver(pre_save, sender=Publication)
# def save_authors(sender, instance, created, **kwargs):
#     if created and getattr(instance,'authors_list',False):
#         instance.authors.add(*instance.authors_list)
#         instance.save()

