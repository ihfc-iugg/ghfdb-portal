from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db import transaction
from django.forms import modelform_factory
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views.generic import DetailView, TemplateView

from .models import Review

# class ReviewDataTable(BaseDataTable, ScrollerMixin):
#     model = Review
#     fields = ["id", "reviewer", "dataset", "nominated", "submitted", "accepted"]
#     stateSave = True
#     fixedHeader = True
#     scrollY = "100vh"
#     scroller = {"loadingIndicator": True}
#     dom = "rti"


def user_review_list(request):
    context = {"review_list": Review.objects.filter(reviewer=request.user)}
    return render(request, "review/review_list.html", context=context)


def user_review(request):
    context = {"publication": Review.objects.filter(reviewer=request.user)}
    return render(request, "review/review_list.html", context=context)


def custodian_accepts_request_to_review(request):
    """Handles the response from the custodian whether a user can become a reviewer.

    1a. accept user and grant required permissions to review publications
    1b. deny user
    2. send email to user informing of decision and why

    """
    # review = Review.objects.filter(pk=review_pk).get()

    return render()


class ReviewDetailView(LoginRequiredMixin, DetailView):
    template_name = "review/detail_view.html"
    model = Review


class EditView(LoginRequiredMixin, DetailView):
    template_name = "review/review.html"
    model = Review

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = modelform_factory(Review, exclude=["reviewer", "dataset"])(instance=self.object)
        return context


def verify_dataset(request, dataset):
    """Allows a reviewer to verify that the dataset is correct and ready for publication"""
    return render()


def submit(request):
    """Allows a reviewer to submit their revised data for acceptance by site admins"""
    return render()


# @requires_custodian
def accept_review(request, review):
    """Allows a site admin to accept a review as complete and copy the data back across to the main database"""
    return render()
