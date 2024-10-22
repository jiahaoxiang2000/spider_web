from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("fail/", views.fail, name="fail"),
    path("status/", views.spider_status, name="spider_status"),
]
