# Generated by Django 5.0.6 on 2024-07-24 02:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crypto', '0004_rename_mymodel_favouritepages_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='favouritepages',
            name='currency',
            field=models.CharField(default='$', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='favouritepages',
            name='time',
            field=models.CharField(default='1 week', max_length=200),
            preserve_default=False,
        ),
    ]
