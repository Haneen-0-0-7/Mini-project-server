# Generated by Django 4.2.1 on 2023-06-19 02:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("setexam", "0014_section_class_name_alter_section_faculty"),
    ]

    operations = [
        migrations.AddField(
            model_name="student",
            name="attendance",
            field=models.BooleanField(default=False),
        ),
    ]
