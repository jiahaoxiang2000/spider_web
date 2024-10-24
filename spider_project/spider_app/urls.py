from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("tasks/", views.tasks, name="tasks"),
    path("change_authority/", views.change_authority, name="change_authority"),
    path("stop_task/<int:task_id>/", views.stop_task, name="stop_task"),
    path("download/<int:task_id>/", views.download_file, name="download_file"),
]
