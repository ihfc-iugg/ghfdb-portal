# Generated by Django 2.2.24 on 2021-10-27 08:51

from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0010_auto_20211027_1732'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customfile',
            name='publication',
        ),
        migrations.RemoveField(
            model_name='customlink',
            name='publication',
        ),
        migrations.DeleteModel(
            name='List',
        ),
        migrations.AddField(
            model_name='publication',
            name='booktitle',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AlterField(
            model_name='publication',
            name='ENTRYTYPE',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='publication',
            name='author',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
        migrations.AlterField(
            model_name='publication',
            name='citekey',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name='publication',
            name='keywords',
            field=taggit.managers.TaggableManager(help_text=None, through='publications.UUIDTaggedItem', to='taggit.Tag', verbose_name='key words'),
        ),
        migrations.AlterField(
            model_name='publication',
            name='url',
            field=models.URLField(blank=True, verbose_name='URL'),
        ),
        migrations.DeleteModel(
            name='CustomFile',
        ),
        migrations.DeleteModel(
            name='CustomLink',
        ),
    ]