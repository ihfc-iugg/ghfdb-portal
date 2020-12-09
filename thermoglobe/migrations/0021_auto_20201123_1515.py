# Generated by Django 3.1.3 on 2020-11-23 04:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thermoglobe', '0020_delete_custompublication'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='year_drilled',
            field=models.IntegerField(blank=True, null=True, verbose_name='year drilled'),
        ),
        migrations.AlterField(
            model_name='historicalpublication',
            name='bib_id',
            field=models.CharField(blank=True, db_index=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='historicalpublication',
            name='doi',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='historicalpublication',
            name='journal',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AlterField(
            model_name='historicalpublication',
            name='source',
            field=models.CharField(blank=True, default='User Upload', max_length=128),
        ),
        migrations.AlterField(
            model_name='historicalpublication',
            name='title',
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name='historicalpublication',
            name='type',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='publication',
            name='bib_id',
            field=models.CharField(blank=True, max_length=128, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='publication',
            name='doi',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='publication',
            name='journal',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AlterField(
            model_name='publication',
            name='source',
            field=models.CharField(blank=True, default='User Upload', max_length=128),
        ),
        migrations.AlterField(
            model_name='publication',
            name='title',
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name='publication',
            name='type',
            field=models.CharField(blank=True, max_length=128),
        ),
    ]