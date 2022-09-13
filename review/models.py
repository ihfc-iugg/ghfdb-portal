from django.db import models
from database.models.models import SiteAbstract, IntervalAbstract
from django.utils.translation import gettext as _


# Create your models here.
class Review(models.Model):
    reviewer = models.OneToOneField("user.User", 
    help_text=_('User reviewing this publication'),
    on_delete=models.SET_NULL,
    null=True)
    nominated = models.DateTimeField(_('reviewer nominated'), auto_now_add=True,
    help_text=_('Date the user nominated themselves to review this publication'),
    )
    accepted = models.DateTimeField(_('review accepted'),
    help_text=_('Date the review was accepted by site admins and incorporated into the production database'),
    null=True, blank=True,
    )
    submitted = models.DateTimeField(_('review submitted'),
    help_text=_('Date the user submitted correction for final approval by site admins'),
    null=True, blank=True)
    publication = models.OneToOneField("publications.Publication", 
    help_text=_('Publication being review'),
    on_delete=models.SET_NULL, null=True)


class ReviewSite(SiteAbstract):
    class Meta(SiteAbstract.Meta):
        db_table = 'site_review'
        default_related_name = 'review_sites'


class ReviewInterval(IntervalAbstract):

    site = models.ForeignKey("review.ReviewSite",
                verbose_name=_("site"),
                null=True,
                on_delete=models.SET_NULL)

    class Meta(IntervalAbstract.Meta):
        db_table = 'heat_flow_interval_review'
        default_related_name = 'review_intervals'

    def save(self, force_insert, force_update, using, update_fields):
        return super().save(force_insert, force_update, using, update_fields)
