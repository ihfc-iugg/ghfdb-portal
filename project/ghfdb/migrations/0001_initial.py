# Generated by Django 5.1.6 on 2025-06-20 13:40

import django.db.models.manager
import django_bleach.models
import django_lifecycle.mixins
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="GHFDBRelease",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "added",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="The date and time this record was added to the database.",
                        verbose_name="Date added",
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="The date and time this record was last modified.",
                        verbose_name="Last modified",
                    ),
                ),
                (
                    "version",
                    models.CharField(
                        max_length=50, unique=True, verbose_name="Version"
                    ),
                ),
                ("release_date", models.DateField(verbose_name="Release Date")),
                (
                    "description",
                    django_bleach.models.BleachField(
                        blank=True, verbose_name="Description"
                    ),
                ),
                (
                    "file",
                    models.FileField(
                        upload_to="ghfdb/releases/", verbose_name="Release File"
                    ),
                ),
            ],
            options={
                "verbose_name": "GHFDB Release",
                "verbose_name_plural": "GHFDB Releases",
                "ordering": ["-release_date"],
            },
            bases=(django_lifecycle.mixins.LifecycleModelMixin, models.Model),
            managers=[
                ("objects", django.db.models.manager.Manager()),
                ("prefetch_manager", django.db.models.manager.Manager()),
            ],
        ),
    ]
