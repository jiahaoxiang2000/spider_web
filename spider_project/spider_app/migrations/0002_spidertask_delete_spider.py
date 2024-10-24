# Generated by Django 5.1.2 on 2024-10-23 12:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("spider_app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SpiderTask",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("username", models.CharField(max_length=100)),
                ("password", models.CharField(max_length=100)),
                ("date", models.CharField(max_length=10)),
                ("country_code", models.CharField(max_length=10)),
                ("token", models.CharField(blank=True, max_length=100)),
                ("current_page", models.IntegerField(default=1)),
                ("total_page", models.IntegerField()),
                ("done", models.BooleanField(default=False)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.DeleteModel(
            name="Spider",
        ),
    ]
