import json
from ..gfz_dataservices.models import License, Schema

def get_licenses():
    return [(l, l) for l in License.objects.values_list('name',flat=True)]
