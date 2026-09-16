"""The assessment description form (T015, plan.md "The pages", spec.md User
Story 2).

Publication, assessors, dates and an optional title, collected before any
file is chosen (FR-003 through FR-007).
"""

from django import forms
from django.utils.translation import gettext as _
from django_select2.forms import Select2MultipleWidget, Select2Widget
from fairdm.contrib.contributors.models import Person
from fairdm.forms import ModelForm
from literature.models import LiteratureItem
from partial_date import PartialDate

from .models import Review


class ReviewDescriptionForm(ModelForm):
    literature = forms.ModelChoiceField(
        queryset=LiteratureItem.objects.all(),
        required=True,
        label=_("Publication"),
        help_text=_("The publication the assessed data comes from."),
        widget=Select2Widget,
    )

    reviewers = forms.ModelMultipleChoiceField(
        queryset=Person.objects.real(),
        required=True,
        label=_("Assessors"),
        help_text=_(
            "The people who carried out the assessment. Any contributor "
            "profile may be named, whether or not it holds a portal account."
        ),
        widget=Select2MultipleWidget,
    )

    title = forms.CharField(
        required=False,
        label=_("Title"),
        help_text=_(
            "The dataset's title. Leave blank to use the publication's own title."
        ),
    )

    class Meta:
        model = Review
        fields = ["literature", "reviewers", "start_date", "end_date", "title"]

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if start_date and end_date and PartialDate(end_date) < PartialDate(start_date):
            self.add_error(
                "end_date",
                _("The end date (%(end)s) cannot be before the start date (%(start)s).")
                % {"end": end_date, "start": start_date},
            )
        return cleaned_data
