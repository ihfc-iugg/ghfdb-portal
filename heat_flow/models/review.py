"""
Global Heat Flow Database (GHFDB) models for Django. The models are defined using the Django ORM and are used to create the database schema. The models are defined using the following sources:

    - Fuchs et. al., (2021). A new database structure for the IHFC Global Heat Flow Database. International Journal of
    Terrestrial Heat Flow and Applications, 4(1), pp.1-14.

    - Fuchs et. al. (2023). The Global Heat Flow Database: Update 2023.

"""

from django.conf import settings
from django.db import models as dj_models
from django.utils.translation import gettext as _
from fairdm.core.models import Dataset
from fairdm.db import models
from partial_date.fields import PartialDateField


class Review(dj_models.Model):
    reviewers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("reviewers"),
        help_text=_("Users who have reviewed the data."),
        related_name="heat_flow_reviews",
    )

    dataset = models.OneToOneField(
        "fairdm_core.Dataset",
        verbose_name=_("dataset"),
        help_text=_("The dataset that was reviewed."),
        on_delete=models.CASCADE,
        related_name="review",
    )

    literature = models.OneToOneField(
        "literature.LiteratureItem",
        verbose_name=_("literature"),
        help_text=_("The literature item that was reviewed."),
        on_delete=models.CASCADE,
        related_name="review",
    )

    start_date = PartialDateField(
        verbose_name=_("start date"),
        help_text=_("Date the review started."),
    )

    completion_date = PartialDateField(
        verbose_name=_("completion date"),
        help_text=_("Date the review was completed."),
        null=True,
        blank=True,
    )

    status = models.IntegerField(
        choices=[
            (1, _("Review pending")),
            (2, _("Review accepted")),
            (0, _("Review rejected")),
        ],
        default=1,
        verbose_name=_("status"),
        help_text=_("The status of the review."),
    )

    comment = models.TextField(
        verbose_name=_("comment"),
        help_text=_("General comment on the review."),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")
        ordering = ["-start_date"]

    def save(self, *args, **kwargs):
        if not kwargs.get("pk") and not self.dataset_id:
            self.dataset = Dataset.objects.create(name=self.literature.title)
        super().save(*args, **kwargs)
