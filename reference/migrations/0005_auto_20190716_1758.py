# Generated by Django 2.2.1 on 2019-07-16 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0004_auto_20190716_1755'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filestorage',
            name='date_added',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]