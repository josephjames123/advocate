# Generated by Django 4.2.1 on 2024-01-16 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0098_holidayrequest_timing'),
    ]

    operations = [
        migrations.AddField(
            model_name='lawyerprofile',
            name='additional_qualification_documents',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='holidayrequest',
            name='type',
            field=models.CharField(choices=[('dutyleave', 'Duty Leave'), ('casual_leave', 'Casual Leave')], max_length=20),
        ),
    ]