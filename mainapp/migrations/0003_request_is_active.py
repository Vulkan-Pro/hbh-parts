# Generated by Django 2.2.6 on 2020-04-19 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0002_response'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
