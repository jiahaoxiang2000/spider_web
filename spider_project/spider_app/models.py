from django.db import models


# Create your models here.
class Spider(models.Model):
    class Meta:
        app_label = "spider_app"

    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    date = models.CharField(max_length=10)
    country_code = models.CharField(max_length=10)
    token = models.CharField(max_length=100, blank=True)
    page_number = models.IntegerField()
    failure_reason = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
