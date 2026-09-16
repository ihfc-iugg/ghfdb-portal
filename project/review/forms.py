"""The assessment description form (T015, plan.md "The pages", spec.md User
Story 2).

Publication, assessors, dates and an optional title, collected before any
file is chosen (FR-003 through FR-007).
"""

import json

from django import forms
from django.core.exceptions import ValidationError
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
        required=False,
        label=_("Publication"),
        help_text=_(
            "The publication the assessed data comes from, found in the "
            "catalogue. Leave blank and supply a bibliography file below "
            "when it is not there yet."
        ),
        widget=Select2Widget,
    )

    bibliography_file = forms.FileField(
        required=False,
        label=_("Bibliography file"),
        help_text=_(
            "A CSL-JSON bibliography record for the publication, used "
            "instead of the field above to add it to the catalogue without "
            "leaving this form."
        ),
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
        fields = [
            "literature",
            "reviewers",
            "start_date",
            "end_date",
            "title",
            "bibliography_file",
        ]

    def clean_bibliography_file(self):
        bibliography_file = self.cleaned_data.get("bibliography_file")
        if not bibliography_file:
            return bibliography_file
        try:
            data = json.loads(bibliography_file.read().decode("utf-8"))
        except (ValueError, UnicodeDecodeError) as exc:
            raise ValidationError(
                _("This is not a valid bibliography record."), code="invalid"
            ) from exc
        if not isinstance(data, dict):
            raise ValidationError(
                _("This is not a valid bibliography record."), code="invalid"
            )
        return data

    def clean(self):
        cleaned_data = super().clean()

        literature = cleaned_data.get("literature")
        bibliography_data = cleaned_data.get("bibliography_file")
        if not literature and bibliography_data:
            literature = LiteratureItem.objects.create(item=bibliography_data)
            cleaned_data["literature"] = literature
        elif not literature and not self.has_error("bibliography_file"):
            self.add_error(
                "literature",
                _(
                    "Choose a publication from the catalogue, or add one "
                    "from a bibliography file."
                ),
            )

        if literature:
            existing = Review.objects.filter(literature=literature)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            existing = existing.first()
            if existing:
                self.add_error(
                    "literature",
                    _("%(literature)s already has an assessment: %(title)s.")
                    % {"literature": literature, "title": existing.dataset.name},
                )

        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if start_date and end_date and PartialDate(end_date) < PartialDate(start_date):
            self.add_error(
                "end_date",
                _("The end date (%(end)s) cannot be before the start date (%(start)s).")
                % {"end": end_date, "start": start_date},
            )
        return cleaned_data
