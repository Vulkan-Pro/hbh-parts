# Generated by Django 2.2.6 on 2020-04-26 23:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0010_match_engagement_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='propertyentry',
            name='property_number',
        ),
        migrations.AddField(
            model_name='propertyentry',
            name='property_title',
            field=models.CharField(blank=True, max_length=10, null=True, unique=True),
        ),
    ]