from .models import Field, Page
from import_export import resources

class FieldResource(resources.ModelResource):

    class Meta:
        model = Field
        fields = [
            'id',
            'field_name',
            'description',
            'units',          
            ]

class PageResource(resources.ModelResource):

    class Meta:
        model = Page
        fields = [
            'id',
            'heading',
            'sub_heading',
            'content',          
            ]


