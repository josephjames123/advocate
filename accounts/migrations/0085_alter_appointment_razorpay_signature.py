# Generated by Django 4.2.4 on 2023-09-26 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0084_remove_appointment_payment_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='razorpay_signature',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
