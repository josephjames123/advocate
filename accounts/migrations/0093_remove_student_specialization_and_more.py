# Generated by Django 4.2.4 on 2023-10-04 04:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0092_remove_task_case_task_work_assignment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='specialization',
        ),
        migrations.AlterField(
            model_name='student',
            name='year_of_pass',
            field=models.CharField(blank=True, choices=[('2019', '2019'), ('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('2023', '2023'), ('2024', '2024')], max_length=50, null=True),
        ),
    ]
