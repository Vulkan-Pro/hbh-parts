# Generated by Django 2.2.6 on 2020-05-13 06:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0025_auto_20200513_0324'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='match',
            unique_together={('buyer_request', 'property_entry')},
        ),
    ]
