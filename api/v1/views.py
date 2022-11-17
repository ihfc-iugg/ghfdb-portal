from database.models import HeatFlow, Interval
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.renderers import TemplateHTMLRenderer
from geoluminate.views import FieldSetMixin


class MapPopupTemplate(FieldSetMixin, generics.RetrieveAPIView):
    """
    A view that returns a templated HTML representation of a given site.
    """
    queryset = HeatFlow.objects.all()
    renderer_classes = [TemplateHTMLRenderer]
    schema = None
    fieldset = [
        (None,
            {'fields': [
                'q',
                'q_unc',
                'method',
                'env',
                'expl',
                'wat_temp',
                'q_comment',
            ]}),
        # ('Geographic',
        #     {'fields': [
        #         'country',
        #         'political',
        #         'continent',
        #         'ocean',
        #         'province',
        #         'plate',
        #         ]}),
    ]

    def get(self, request, *args, **kwargs):
        context = dict(
            site=self.get_object(),
            fieldset=self.get_fieldset(),
        )
        return Response(context, template_name='api/map_popup.html')
