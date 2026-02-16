from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator as MaxVal
from django.core.validators import MinValueValidator as MinVal
from django.utils.translation import gettext as _
from fairdm.core.models import Measurement
from fairdm.db import models


class ParentHeatFlow(Measurement):
    """Database table that stores terrestrial heat flow data. This is the "parent" schema outlined in the formal structure of the database put forth by Fuchs et al (2021)."""

    value = models.QuantityField(
        verbose_name=_("heat flow"),
        base_units="mW / m^2",
        help_text=_(
            "Heat-flow density at a given location after all corrections for instrumental and environmental effects have been applied."
        ),
        validators=[MinVal(-(10**6)), MaxVal(10**6)],
    )
    uncertainty = models.QuantityField(
        base_units="mW / m^2",
        verbose_name=_("uncertainty"),
        help_text=_(
            "Uncertainty (one standard deviation) of the heat-flow value estimated by error propagation from"
            " uncertainty in thermal conductivity and temperature gradient, standard deviation from the average of the"
            " heat flow intervals or deviation from the linear regression of the Bullard plot."
        ),
        validators=[MinVal(0), MaxVal(10**6)],
        blank=True,
        null=True,
    )
    corr_HP_flag = models.BooleanField(
        verbose_name=_("HP correction flag"),
        help_text=_(
            "Specifies if corrections to the calculated heat flow considers the contribution of the heat production of"
            " the overburden to the terrestrial surface heat flow q."
        ),
        null=True,
        blank=True,
        default=None,
    )
    comment = models.TextField(
        verbose_name=_("comment"),
        help_text=_("General comments on the parent level."),
        blank=True,
        null=True,
    )

    children = models.ManyToManyField(
        "heat_flow.HeatFlow",
        related_name="parent",
        through="ghfdb.ParentChildRelation",
        verbose_name=_("child heat flows"),
        help_text=_("Child heat flow measurements that contribute to this parent heat flow value."),
    )


    class Meta:
        verbose_name = _("Heat Flow")
        verbose_name_plural = _("Heat Flow")
        db_table_comment = "Heat flux at Earth's surface for a given HeatFlowSite. This table roughly correlates to the parent level of the GHFDB schema."
        indexes = [
            models.Index(fields=["is_ghfdb"]),
            models.Index(fields=["corr_HP_flag"]),
        ]
        constraints = [
            # Note: Constraints with Quantity fields are commented out due to SQLite compatibility issues
            # The validators on the fields themselves provide the same validation
            # models.CheckConstraint(
            #     condition=models.Q(uncertainty__gte=0) | models.Q(uncertainty__isnull=True),
            #     name="non_negative_surface_uncertainty",
            # ),
        ]

    def save(self, *args, **kwargs):
        # Enforce one parent per site
        if self.sample_id:
            existing = ParentHeatFlow.objects.filter(
                sample=self.sample
            ).exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError(
                    f"A ParentHeatFlow already exists for site {self.sample}. "
                    f"Only one parent per site is allowed."
                )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.value}"

    @property
    def site(self):
        return self.sample

    def get_quality(self):
        """From Fuchs et al 2023 - Quality-assurance of heat-flow data: The new structure and evaluation scheme of the IHFC Global Heat Flow Database (Section 3.4 - Evaluation of the site-specific HFD quality on the parent level).

        >So far, the evaluation scheme was applied on the child level only. To provide a quality score on the parent level, several cases need to be distinguished. First, if only one child element is present, the score of this entry is simply passed to the parent level. Secondly, if more than one child element is present and all child elements were considered in the calculation of the site-specific HFD value, the poorest ranking is inherited to the parent level (Fig. 5). Thirdly, if more than one child element is present but not all of them were used to calculate a site-specific HFD, only the ones used are considered and the poorest ranking of the relevant child elements is inherited to the parent level again (cf. underlines in Fig. 5).
        """
        relevant = self.children.filter(
            parentchildrelation__is_relevant=True
        )
        count = relevant.count()
        if count == 0:
            return None
        elif count == 1:
            return relevant.first().get_quality()
        else:
            return relevant.order_by("quality").first().get_quality()


class ParentChildRelation(models.Model):
    """
    Intermediate model to represent the many-to-many relationship between ParentHeatFlow and HeatFlow (child).
    This model allows for additional fields to be added to the relationship in the future if needed.
    """

    parent = models.ForeignKey(
        "ghfdb.ParentHeatFlow",
        on_delete=models.CASCADE,
        verbose_name=_("parent heat flow"),
    )
    child = models.ForeignKey(
        "heat_flow.HeatFlow",
        on_delete=models.CASCADE,
        verbose_name=_("child heat flow"),
        unique=True,
    )

    is_relevant = models.BooleanField(
        verbose_name=_("is relevant"),
        help_text=_("Indicates whether this child heat flow measurement was used in the calculation of the parent heat flow value."),
        default=False,
    )

    class Meta:
        verbose_name = _("Parent-Child Heat Flow Relation")
        verbose_name_plural = _("Parent-Child Heat Flow Relations")
        unique_together = ("parent", "child")


class GHFDBRelease(models.Model):
    """
    Model to represent a release of the Global Heat Flow Database (GHFDB).
    This model is used to track different versions of the GHFDB.
    """

    version = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Version"),
    )
    release_date = models.DateField(
        verbose_name=_("Release Date"),
    )
    description = models.TextField(
        verbose_name=_("Description"),
        blank=True,
    )
    file = models.FileField(
        upload_to="ghfdb/releases/",
        verbose_name=_("Release File"),
    )

    class Meta:
        verbose_name = _("GHFDB Release")
        verbose_name_plural = _("GHFDB Releases")
        ordering = ["-release_date"]
