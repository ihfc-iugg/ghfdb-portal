# Generated by Django 2.2.1 on 2019-07-16 08:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reference', '0002_auto_20190705_1351'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileStorage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.FileField(upload_to='data/%Y/%m/')),
                ('description', models.TextField(blank=True, null=True)),
                ('first_name', models.CharField(max_length=150)),
                ('last_name', models.CharField(max_length=150)),
                ('date_uploaded', models.DateTimeField()),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('added_by', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]