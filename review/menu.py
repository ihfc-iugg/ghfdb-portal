from geoluminate.menus import Menu, Node
from django.urls import reverse, resolve
from django.utils.translation import gettext_lazy as _
from django.urls import reverse, resolve, path
from django.views.generic import DetailView
from .models import Review


class PubNode(Node):
    base_template_name = "review/hx/"
    model = Review

    def url_pattern(self):
        return path(f'{self.name}/',
                    DetailView.as_view(
                        template_name=f"{self.base_template_name}{self.name}.html",
                        model=self.model),
                    name=self.name)


class ReviewMenu(Menu):

    def nodes(self):
        return [
            PubNode('reference', icon='fa-book', object=self.object),
            PubNode('data', icon='fa-table', object=self.object),
            PubNode('map', icon='fa-map', object=self.object),
            PubNode('review', icon='fa-history', object=self.object),
        ]
