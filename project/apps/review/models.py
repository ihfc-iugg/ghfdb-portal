from django.db import models
from django.utils.translation import gettext as _
from ghfdb.models import HeatFlow, Interval


class Review(models.Model):
    """Stores information about each review"""

    reviewer = models.ForeignKey(
        to="user.User",
        help_text=_("User reviewing this publication"),
        on_delete=models.SET_NULL,
        null=True,
    )
    nominated = models.DateTimeField(
        verbose_name=_("reviewer nominated"),
        auto_now_add=True,
        help_text=_("Date the user nominated themselves to review this publication"),
    )
    accepted = models.DateTimeField(
        verbose_name=_("review accepted"),
        help_text=_(
            "Date the review was accepted by site admins and incorporated into the production database"
        ),
        null=True,
        blank=True,
    )
    submitted = models.DateTimeField(
        verbose_name=_("review submitted"),
        help_text=_(
            "Date the user submitted correction for final approval by site admins"
        ),
        null=True,
        blank=True,
    )
    publication = models.OneToOneField(
        to="literature.Literature",
        help_text=_("Publication being reviewed"),
        on_delete=models.SET_NULL,
        null=True,
    )

    def __str__(self):
        return f"Review of {self.publication} by {self.reviewer}"


class HeatFlowReview(HeatFlow):
    hide_from_api = True
    review_of = models.OneToOneField(
        "ghfdb.HeatFlow",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="revised",
    )

    review = models.ForeignKey(Review, on_delete=models.CASCADE)

    class Meta:
        db_table = "heat_flow_review"


class IntervalReview(Interval):
    hide_from_api = True

    review_of = models.OneToOneField(
        "ghfdb.Interval",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="revised",
    )
    review = models.ForeignKey(Review, on_delete=models.CASCADE)

    class Meta:
        db_table = "interval_review"
