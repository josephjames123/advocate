# Generated by Django 4.2.4 on 2023-09-09 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0036_alter_lawyerprofile_working_time_end_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lawyerprofile',
            name='working_time_end',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='lawyerprofile',
            name='working_time_start',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
