# Generated by Django 2.2.6 on 2020-05-09 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0014_auto_20200501_0149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='engagement_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Declined', 'Declined'), ('Completed', 'Completed'), ('Archived', 'Archived')], default='Pending', max_length=20),
        ),
    ]
