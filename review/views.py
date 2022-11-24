from django.shortcuts import render, get_object_or_404, redirect
from django.forms.models import model_to_dict
from .models import Review, HeatFlowReview, IntervalReview, HeatFlow, Interval
from literature.models import Publication
from django.forms import modelform_factory
from django.core.mail import send_mail
from literature.views import PublicationList
from django.views.generic import TemplateView, DetailView
from user.forms import SocialSignupForm
from django.utils.translation import gettext as _
from allauth.account.forms import AddEmailForm
from allauth.account.utils import has_verified_email
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from .menu import ReviewMenu

# HeatFlowForm = modelform_factory(HeatFlow, fields='__all__')
# HeatFlowReviewForm = modelform_factory(HeatFlowReview, fields='__all__')
# IntervalForm = modelform_factory(Interval, fields='__all__')
# IntervalReviewForm = modelform_factory(IntervalReview, fields='__all__')


class ReviewList(PublicationList):
    """
    Display an individual :model:`myapp.MyModel`.

    **Context**

    ``mymodel``
        An instance of :model:`myapp.MyModel`.

    **Template:**

    :template:`review/publication.html`
    """
    model = Publication
    publication_template = 'review/publication.html'
    template_name = 'review/list.html'
    paginate_by = 50
    # filterset_class = PublicationFilter


def user_review_list(request):
    context = {
        'review_list': Review.objects.filter(reviewer=request.user)
    }
    return render(request, 'review/review_list.html', context=context)


def user_review(request):
    context = {
        'publication': Review.objects.filter(reviewer=request.user)
    }
    return render(request, 'review/review_list.html', context=context)


class BecomeReviewer(LoginRequiredMixin, TemplateView):
    template_name = 'review/become_a_reviewer.html'
    form_class = SocialSignupForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        forms = []
        if not user.orcid:
            # user has not connected their orcid account
            forms.append(
                (_('Account Connections'),
                 "socialaccount/connections.html",
                 None))

        if not has_verified_email(user):
            forms.append(
                (_('E-mail Addresses'),
                    "account/email.html",
                    AddEmailForm(self.request))
            )

        context["forms"] = forms
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if context['forms']:
            return self.render_to_response(context)

        send_mail(
            f'{request.user} wants to become a reviewer for the world heat flow database review project',
            'Click this link to accept or this link to reject the incoming request',
            'from@yourdjangoapp.com',
            ['DATABASE_CUSTODIAN'],
            fail_silently=False,
        )
        # return render(request, "gfz_dataservices/form.html")

# @requires_custodian


def custodian_accepts_request_to_review(request):
    """Handles the response from the custodian whether a user can become a reviewer.

    1a. accept user and grant required permissions to review publications
    1b. deny user
    2. send email to user informing of decision and why

    """
    # review = Review.objects.filter(pk=review_pk).get()

    return render()


@transaction.atomic
def nominate_to_review_publication(request, pk):
    """Accepts an incoming nomination from a reviewer to review a particular publication"""

    ReviewForm = modelform_factory(Review, fields='__all__')

    form = ReviewForm({
        "reviewer": request.user,
        'publication': get_object_or_404(Publication, pk=pk)
    })
    if form.is_valid():
        review = form.save()

    # 2. Get related sites and copy to review table
    for hf in review.publication.sites.all():
        data = model_to_dict(hf)
        data['review_of'] = data.pop('id')
        data['review'] = review
        form = HeatFlowReviewForm(data)
        form.is_valid()
        form.save()

    # 3. Get related intervals and copy to review tables
    for i in review.publication.intervals.all():
        data = model_to_dict(i)
        data['review_of'] = data.pop('id')
        data['review'] = review
        form = IntervalReviewForm(data)
        form.is_valid()
        form.save()

    # 4. either redirect to review list page or provide message to user with
    # link to review page.

    return redirect("review:edit", pk=review.pk)


class EditView(LoginRequiredMixin, DetailView):
    template_name = 'review/review.html'
    model = Review

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['app_menu'] = ReviewMenu(context['object'])
        return context


def submit(request):
    """Allows a reviewer to submit their revised data for acceptance by site admins"""
    return render()


# @requires_custodian
def accept_review(request, review):
    """Allows a site admin to accept a review as complete and copy the data back across to the main database"""
    return render()
