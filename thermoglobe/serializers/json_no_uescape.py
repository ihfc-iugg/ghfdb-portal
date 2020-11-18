from django.core.serializers.json import *

class Serializer(Serializer):

    def _init_options(self):
        super(Serializer, self)._init_options()
        self.json_kwargs['ensure_ascii'] = False