"""
Test Models for Validation Testing

These models simulate the actual GHFDB models for testing validation logic.
"""

from django.db import models


class TestSample(models.Model):
    """Test model simulating Sample model with GHFDB fields."""

    # Site Metadata
    name = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    elevation = models.FloatField(null=True, blank=True)
    location_quality = models.CharField(max_length=50, null=True, blank=True)

    # Measurement Data
    heat_flow = models.FloatField()
    heat_flow_uncertainty = models.FloatField(null=True, blank=True)
    method = models.CharField(max_length=200)
    measurement_date = models.DateField(null=True, blank=True)
    depth_top = models.FloatField(null=True, blank=True)
    depth_bottom = models.FloatField(null=True, blank=True)
    temperature_gradient = models.FloatField(null=True, blank=True)
    thermal_conductivity = models.FloatField(null=True, blank=True)

    # Quality Indicators
    correction_applied = models.BooleanField(default=False)

    # Data Provenance (foreign keys)
    data_source = models.ForeignKey("TestDataSource", null=True, blank=True, on_delete=models.SET_NULL)
    publication = models.ForeignKey("TestPublication", null=True, blank=True, on_delete=models.SET_NULL)

    # Many-to-many
    contributors = models.ManyToManyField("TestContributor", blank=True)

    # Extensions (non-canonical)
    review_status = models.CharField(max_length=50, default="pending")
    internal_notes = models.TextField(blank=True)

    class Meta:
        app_label = "test_validation"

    def calculate_quality_score(self):
        """Computed quality score based on Fuchs et al. 2023."""
        score = 5.0  # Base score
        if self.location_quality == "High":
            score += 2.0
        if self.correction_applied:
            score += 1.0
        if self.heat_flow_uncertainty:
            score += 1.0
        return min(score, 10.0)


class TestDataSource(models.Model):
    """Test model for data source references."""

    citation = models.TextField()

    class Meta:
        app_label = "test_validation"


class TestPublication(models.Model):
    """Test model for publication references."""

    doi = models.CharField(max_length=200, unique=True)
    title = models.TextField()

    class Meta:
        app_label = "test_validation"


class TestContributor(models.Model):
    """Test model for contributors."""

    orcid = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)

    class Meta:
        app_label = "test_validation"


class TestIncompleteSample(models.Model):
    """Test model missing several required GHFDB fields."""

    name = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    # Missing: heat_flow, method, correction_applied, etc.

    class Meta:
        app_label = "test_validation"
