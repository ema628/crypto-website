# Generated by Django 5.0.6 on 2024-07-24 05:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crypto', '0005_favouritepages_currency_favouritepages_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='favouritepages',
            name='idnum',
            field=models.CharField(default=0, max_length=200),
            preserve_default=False,
        ),
    ]
