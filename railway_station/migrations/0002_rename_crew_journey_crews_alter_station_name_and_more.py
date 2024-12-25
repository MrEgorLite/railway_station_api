# Generated by Django 5.1.4 on 2024-12-24 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("railway_station", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="journey",
            old_name="crew",
            new_name="crews",
        ),
        migrations.AlterField(
            model_name="station",
            name="name",
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name="traintype",
            name="name",
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
