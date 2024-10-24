# models.py
from django.db import models


class SpiderTask(models.Model):
    class Meta:
        app_label = "spider_app"

    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    date = models.CharField(max_length=10)
    country = models.CharField(max_length=10)
    current_page = models.IntegerField(default=1)
    total_page = models.IntegerField()
    done = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    stop_flag = models.BooleanField(default=False)
    data_file_path = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Task {self.id} for {self.username}"
