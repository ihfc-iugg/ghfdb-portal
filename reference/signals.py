from .models import Reference, Author
from django.db.models.signals import post_save
from django.dispatch import receiver
from .widgets import get_author_objects


# signals.py
@receiver(post_save, sender=Reference)
def save_coauthors(sender, instance, created, **kwargs):
    # print('\nPlease lord let this print\n')
    if created and getattr(instance,'co_authors_list',False):
        instance.co_authors.add(*instance.co_authors_list)
        # for author in instance.co_authors_list:
        #     instance.co_authors.add(author)
        instance.save()

