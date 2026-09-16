"""
Global Heat Flow Database (GHFDB) models for Django. The models are defined using the Django ORM and are used to create the database schema. The models are defined using the following sources:

    - Fuchs et. al., (2021). A new database structure for the IHFC Global Heat Flow Database. International Journal of
    Terrestrial Heat Flow and Applications, 4(1), pp.1-14.

    - Fuchs et. al. (2023). The Global Heat Flow Database: Update 2023.

"""

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from fairdm.db import models
from partial_date.fields import PartialDateField

from .states import States


class Review(models.Model):
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("uploaded by"),
        help_text=_(
            "The person who created this assessment. Object permissions follow "
            "this person rather than the assessor list, because an assessor may "
            "be an unclaimed profile with no account."
        ),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_reviews",
    )

    state = models.IntegerField(
        choices=States.choices,
        default=States.DESCRIBED,
        verbose_name=_("state"),
        help_text=_("Where this assessment has got to."),
    )

    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("decided by"),
        help_text=_("The Data Curator who approved or sent back this assessment."),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="decided_reviews",
    )

    decided_at = models.DateTimeField(
        verbose_name=_("decided at"),
        help_text=_("When the decision on this assessment was made."),
        null=True,
        blank=True,
    )

    decision_comment = models.TextField(
        verbose_name=_("decision comment"),
        help_text=_("What the curator said when sending this assessment back."),
        blank=True,
    )

    reviewers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("reviewers"),
        help_text=_("Users who have reviewed the data."),
        related_name="heat_flow_reviews",
    )

    dataset = models.OneToOneField(
        "dataset.Dataset",
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
        help_text=_("Date the review was started."),
        null=True,
        blank=True,
    )

    end_date = PartialDateField(
        verbose_name=_("completion date"),
        help_text=_("Date the review was completed."),
        null=True,
        blank=True,
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
        ordering = ["-end_date"]

    def save(self, *args, **kwargs):
        # if not kwargs.get("pk") and not self.dataset_id:
        # self.dataset = Dataset.objects.create(name=self.literature.title)
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError(_("Start date cannot be after end date."))
        super().save(*args, **kwargs)

    @property
    def current(self):
        """The most recent submitted file, or ``None`` if none has been
        submitted yet (data-model.md "review.SubmittedFile")."""
        return self.submissions.order_by("-submitted_at", "-pk").first()


def submission_upload_path(instance, filename):
    """Scope a submitted file's storage path to its assessment."""
    return f"review/submissions/{instance.review_id}/{filename}"


class SubmittedFile(models.Model):
    """One completed upload template as supplied, kept against its
    assessment (T007, data-model.md "review.SubmittedFile").

    A row per submission rather than a field on ``Review``: a curator can
    send an assessment back, and the replacement must not erase what was
    rejected (FR-015).
    """

    review = models.ForeignKey(
        Review,
        verbose_name=_("assessment"),
        help_text=_("The assessment this file was submitted against."),
        on_delete=models.CASCADE,
        related_name="submissions",
    )

    file = models.FileField(
        upload_to=submission_upload_path,
        verbose_name=_("file"),
        help_text=_("The completed upload template as supplied."),
    )

    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("submitted by"),
        help_text=_("Who submitted this file."),
        on_delete=models.PROTECT,
        related_name="submitted_files",
    )

    submitted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("submitted at"),
        help_text=_("When this file was submitted."),
    )

    imported_at = models.DateTimeField(
        verbose_name=_("imported at"),
        help_text=_(
            "When this file's contents were written. Null means checked but "
            "never confirmed."
        ),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Submitted file")
        verbose_name_plural = _("Submitted files")
        ordering = ["-submitted_at"]
