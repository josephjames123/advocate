# Generated by Django 4.2.4 on 2023-09-09 13:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0035_timeslot_booking_booking_date_booking_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lawyerprofile',
            name='working_time_end',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lawyer_end_time', to='accounts.timeslot'),
        ),
        migrations.AlterField(
            model_name='lawyerprofile',
            name='working_time_start',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lawyer_start_time', to='accounts.timeslot'),
        ),
    ]