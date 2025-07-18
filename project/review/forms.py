from django import forms
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django_addanother.widgets import AddAnotherWidgetWrapper
from django_filters import FilterSet
from django_select2 import forms as s2forms
from django_select2.forms import Select2Widget
from fairdm.contrib.contributors.models import Person
from fairdm.forms import ModelForm
from literature.models import LiteratureItem
from martor.fields import MartorFormField

from .models import Review


class ReviewFilterSet(FilterSet):
    class Meta:
        model = LiteratureItem
        fields = ["review__status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ContributorWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        "name__icontains",
        "alternative_names__icontains",
        "identifiers__value__icontains",
    ]


class ReviewForm(ModelForm):
    literature = forms.ModelChoiceField(
        queryset=LiteratureItem.objects.all(),
        required=True,
        label=_("Literature"),
        help_text=_("The current review is associated with the selected literature item. This cannot be changed."),
        widget=Select2Widget,
        disabled=True,
    )

    reviewers = forms.ModelMultipleChoiceField(
        queryset=Person.contributors.all(),
        required=True,
        label=_("Reviewers"),
        help_text=_("Select users who have reviewed the data."),
        widget=AddAnotherWidgetWrapper(
            ContributorWidget,
            reverse_lazy("person-create"),
        ),
    )

    class Meta:
        model = Review
        fields = ["literature", "reviewers", "comment", "end_date"]
        form_attrs = {
            "id": "submit-review-form",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.include_media = True
        # self.helper.layout.append(Submit("submit", _("Submit Review")))


class CreateReviewForm(ReviewForm):
    class Meta:
        model = Review
        fields = ["literature", "start_date", "reviewers"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["literature"].help_text = _(
            "You are about to review the above literature item. Please ensure you have access to publication in full before proceeding."
        )
        self.fields["reviewers"].help_text = _(
            "Select all persons that will be involved with this data review. You can change update this later if required."
        )


class SubmitReviewForm(ReviewForm):
    comment = MartorFormField(
        label=_("Comment"),
        help_text=_("Provide any comments or feedback regarding the review."),
        required=False,
    )

    class Meta:
        model = Review
        fields = ["literature", ("start_date", "end_date"), "reviewers", "comment"]
