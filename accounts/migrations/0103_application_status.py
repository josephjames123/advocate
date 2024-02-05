# Generated by Django 4.2.1 on 2024-02-04 06:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0102_remove_studentpayment_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending', max_length=20),
        ),
    ]