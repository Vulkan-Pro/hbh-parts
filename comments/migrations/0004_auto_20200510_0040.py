# Generated by Django 2.2.6 on 2020-05-09 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0003_auto_20200428_0017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='content',
            field=models.TextField(blank=True, max_length=255, null=True),
        ),
    ]
