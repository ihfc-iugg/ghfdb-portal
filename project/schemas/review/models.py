from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _


class Review(models.Model):
    """Stores information about each review"""

    dataset = models.OneToOneField(
        to="project.Dataset",
        help_text=_("Publication being reviewed"),
        on_delete=models.SET_NULL,
        null=True,
    )
    reviewer = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        help_text=_("User reviewing this publication"),
        on_delete=models.SET_NULL,
        null=True,
    )
    nominated = models.DateTimeField(
        verbose_name=_("date started"),
        auto_now_add=True,
        help_text=_("Date the user nominated themselves to review this publication"),
    )
    submitted = models.DateTimeField(
        verbose_name=_("date submitted"),
        help_text=_("Date the user submitted correction for final approval by site admins"),
        null=True,
        blank=True,
    )
    accepted = models.DateTimeField(
        verbose_name=_("date accepted"),
        help_text=_("Date the review was accepted by site admins and incorporated into the production database"),
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Review of {self.dataset} by {self.reviewer}"
