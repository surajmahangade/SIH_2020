# Generated by Django 2.2.2 on 2020-07-30 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='file_download',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=500)),
                ('parent_link', models.CharField(max_length=500)),
                ('url_of_file', models.CharField(max_length=500)),
            ],
        ),
    ]
