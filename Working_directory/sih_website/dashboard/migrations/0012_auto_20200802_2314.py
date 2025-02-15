# Generated by Django 2.2.2 on 2020-08-02 23:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0011_auto_20200802_2246'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historic_data',
            name='data',
        ),
        migrations.AddField(
            model_name='historic_data',
            name='bc_end_date',
            field=models.DateField(default=None),
        ),
        migrations.AddField(
            model_name='historic_data',
            name='bc_start_date',
            field=models.DateField(default=None),
        ),
        migrations.AddField(
            model_name='historic_data',
            name='ex_date',
            field=models.DateField(default=None),
        ),
        migrations.AddField(
            model_name='historic_data',
            name='nd_end_date',
            field=models.DateField(default=None),
        ),
        migrations.AddField(
            model_name='historic_data',
            name='nd_start_date',
            field=models.DateField(default=None),
        ),
        migrations.AddField(
            model_name='historic_data',
            name='pay_date',
            field=models.DateField(default=None),
        ),
        migrations.AddField(
            model_name='historic_data',
            name='rec_date',
            field=models.DateField(default=None),
        ),
        migrations.AddField(
            model_name='historic_data',
            name='security_code',
            field=models.TextField(default=None),
        ),
        migrations.AddField(
            model_name='historic_data',
            name='security_name',
            field=models.TextField(default=None),
        ),
    ]
