from geoluminate.views import FieldSetMixin
from ghfdb.models import HeatFlow, Interval
from rest_framework import generics
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response


class MapPopupTemplate(FieldSetMixin, generics.RetrieveAPIView):
    """
    A view that returns a templated HTML representation of a given site.
    """

    queryset = HeatFlow.objects.all()
    renderer_classes = [TemplateHTMLRenderer]
    schema = None
    fieldset = [
        (
            None,
            {
                "fields": [
                    "q",
                    "q_unc",
                    "method",
                    "environment",
                    "expl",
                    "wat_temp",
                    "q_comment",
                ]
            },
        ),
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
        return Response(context, template_name="api/map_popup.html")
