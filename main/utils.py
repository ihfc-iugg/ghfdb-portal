from .models import Page

def get_page_or_none(name):
    try:
        return Page.objects.get(name=name)
    except Page.DoesNotExist:
        return None

