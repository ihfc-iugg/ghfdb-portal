from .models import Page

def get_page_or_none(id):
    try:
        return Page.objects.get(pk=id)
    except Page.DoesNotExist:
        return None

