# Generated by Django 4.2.1 on 2024-03-01 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0111_trackernotification'),
    ]

    operations = [
        migrations.AddField(
            model_name='trackernotification',
            name='message',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
    ]
