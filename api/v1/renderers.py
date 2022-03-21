from typing import Union, Optional, Mapping, Any

from rest_framework.renderers import JSONRenderer
import ujson
import uuid
from rest_framework_csv.renderers import CSVRenderer, PaginatedCSVRenderer
from rest_framework.pagination import LimitOffsetPagination

class SiteDownloadRenderer(CSVRenderer):
    header = ['site_name', 'latitude', 'longitude',
            "elevation",  "well_depth", "cruise", "seafloor_age",
            "sediment_thickness", "sediment_thickness_type",
            "bottom_water_temp", "year_drilled",
            "description", "date_added", 'web_url','id','references']

    # media_type = 'text/csv'
    media_type = 'text'
