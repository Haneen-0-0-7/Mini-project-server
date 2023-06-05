# Generated by Django 4.2.1 on 2023-06-03 21:10

import django.contrib.postgres.fields.hstore
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0002_alter_faculty_facultyname'),
        ('setexam', '0003_uploadedcsv_remove_yearexam_exam_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Allotment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('students', django.contrib.postgres.fields.hstore.HStoreField()),
                ('class_alloted', models.CharField(max_length=100)),
                ('faculty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='login.faculty')),
            ],
        ),
    ]
