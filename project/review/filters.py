"""Narrowing the assessment list (FR-025).

One list serves every question asked of the assessments — a reader looking
for a publication, an assessor looking at their own, a curator looking at
what is waiting on them — so the questions are filters rather than pages.
The waiting list a curator used to have its own page for is this filter set
with ``state`` chosen.

Each person filter offers only the people who actually appear in that role,
rather than every contributor profile in the portal: the portal holds
thousands of them and all but a handful would match nothing.
"""

import django_filters
from django.utils.translation import gettext_lazy as _

from .models import Review
from .states import States


def _people_who(field_name):
    """A queryset of the people named in *field_name* on some assessment."""

    def queryset(request):
        from django.contrib.auth import get_user_model

        return (
            get_user_model()
            .objects.filter(**{f"{field_name}__isnull": False})
            .distinct()
            .order_by("name")
        )

    return queryset


class ReviewFilter(django_filters.FilterSet):
    state = django_filters.ChoiceFilter(
        choices=States.choices,
        label=_("State"),
        empty_label=_("Any state"),
    )
    reviewers = django_filters.ModelChoiceFilter(
        queryset=_people_who("heat_flow_reviews"),
        label=_("Assessor"),
        empty_label=_("Anyone"),
    )
    uploaded_by = django_filters.ModelChoiceFilter(
        queryset=_people_who("uploaded_reviews"),
        label=_("Uploaded by"),
        empty_label=_("Anyone"),
    )
    decided_by = django_filters.ModelChoiceFilter(
        queryset=_people_who("decided_reviews"),
        label=_("Decided by"),
        empty_label=_("Anyone"),
    )

    class Meta:
        model = Review
        fields = ["state", "reviewers", "uploaded_by", "decided_by"]
