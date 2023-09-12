# Generated by Django 4.2.4 on 2023-09-02 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_rename_lawyer_id_lawyerprofile_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lawyerprofile',
            name='specialization',
            field=models.CharField(choices=[('family Lawyer', 'Family Lawyer'), ('criminal Lawyer', 'Criminal Lawyer'), ('consumer Lawyer', 'Consumer Lawyer')], max_length=20),
        ),
    ]
