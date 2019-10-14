from .models import Reference
from django.db.models.signals import post_save
from .widgets import get_authors
import bibtexparser as bib


# signals.py
@receiver(post_save, sender=Reference)
def group_post_save(sender, instance, created, **kwargs):
    bib_obj = bib.loads(self.bibtex).entries[0]

    co_authors = get_authors(bib_obj['author'])[1:]
    for author in co_authors:
        instance.co_authors.add(author)
