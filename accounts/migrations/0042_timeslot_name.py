# Generated by Django 4.2.4 on 2023-09-11 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0041_lawyerdayoff'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeslot',
            name='name',
            field=models.CharField(default=1, max_length=30),
            preserve_default=False,
        ),
    ]