from datetime import date

import django_filters as df
from actstream import action
from braces.views import GroupRequiredMixin, MessageMixin, SelectRelatedMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext as _
from django.views.generic.edit import UpdateView
from django_select2.forms import Select2Widget
from fairdm import plugins
from fairdm.contrib.contributors.models import Person
from fairdm.core.models import Dataset
from fairdm.utils.filters import LiteratureFilterset
from fairdm.utils.permissions import assign_all_model_perms
from fairdm.views import FairDMCreateView, FairDMListView
from literature.models import LiteratureItem

from .forms import CreateReviewForm, SubmitReviewForm
from .models import Review


class ReviewFilterSet(LiteratureFilterset):
    reviewer = df.ModelChoiceFilter(
        field_name="review__reviewers",
        queryset=Person.contributors.filter(groups__name="reviewers"),
        label=_("Reviewer"),
        widget=Select2Widget,
    )

    class Meta:
        model = LiteratureItem
        fields = ["review__status", "reviewer", "type", "issued", "doi", "title", "author", "o"]


class ReviewListView(SelectRelatedMixin, FairDMListView):
    title = _("GHFDB Review")
    model = LiteratureItem
    filterset_class = ReviewFilterSet
    select_related = ("review",)
    title_config = {
        "icon": "review",
        "text": _("Literature Review"),
    }
    grid_config = {
        "card": "review.card",
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_user_is_reviewer"] = self.request.user.groups.filter(name="reviewers").exists()
        return context


class ReviewCreateView(GroupRequiredMixin, FairDMCreateView):
    group_required = ["reviewers"]
    title = _("Start Review")
    model = Review
    form_class = CreateReviewForm
    fields = ["literature", "start_date", "reviewers"]
    title_config = {
        "text": _("Start Review"),
    }

    def dispatch(self, request, *args, **kwargs):
        literature_id = kwargs.get("literature_id")
        self.literature = get_object_or_404(LiteratureItem, pk=literature_id)
        if Review.objects.filter(literature=self.literature).exists():
            return redirect("review-list")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["initial"] = {
            "literature": self.literature.pk,
            "reviewers": [self.request.user.pk],
        }
        return kwargs

    @transaction.atomic
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.literature = self.literature  # Ensure correct value is saved
        self.object.status = Review.STATUS_CHOICES.PENDING
        self.object.start_date = date.today().isoformat()
        dataset = Dataset.objects.create(
            name=self.object.literature.title,
        )
        self.object.dataset = dataset
        self.object.save()
        form.save_m2m()  # Save many-to-many relationships
        # assign all perms to all reviewers
        # these will be removed when the review is closed
        for reviewer in self.object.reviewers.all():
            assign_all_model_perms(reviewer, dataset)
            # Add the reviewer to the dataset as a DataCurator (ensures they get credit for the review)
            dataset.add_contributor(reviewer, with_roles="DataCurator")
            # add activity for the dataset
            action.send(
                self.request.user,
                verb="started a review",
                target=dataset,
            )

        return redirect(dataset.get_absolute_url())


@plugins.dataset.register
class ReviewSubmitView(plugins.Action, MessageMixin, UpdateView):
    title = _("Submit Review")
    name = "submit-review"
    menu_item = {
        "name": _("Submit Review"),
        "icon": "submit_review",
    }
    model = Review
    form_class = SubmitReviewForm

    @staticmethod
    def check(request, instance, **kwargs):
        return request.user.is_superuser

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"instance": self.object.review})
        kwargs["initial"] = {
            "end_date": date.today().isoformat(),
        }
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        self.messages.success(
            _("Your review of %(title)s has been submitted.") % {"title": self.object.literature.title},
        )
        return response

    def get_success_url(self):
        return self.object.dataset.get_absolute_url()
