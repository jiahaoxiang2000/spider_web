import json
import os
import threading
from time import sleep, time
from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, JsonResponse

from spider_project.spider_project import settings
from .models import SpiderTask
from .forms import SpiderForm
from .spider_logic import SpiderLogic
from .forms import ChangeAuthorityForm
import logging

logger = logging.getLogger(__name__)


def home(request):
    if request.method == "POST":
        form = SpiderForm(request.POST)
        if form.is_valid():
            spider_data = form.cleaned_data
            date = spider_data["date"]
            country = spider_data["country"]
            username = spider_data["username"]
            password = spider_data["password"]

            spider_logic = SpiderLogic(
                {
                    "username": username,
                    "password": password,
                }
            )
            try:
                total_page = spider_logic.get_total_page(date, country)
                # here we start this task, we will save the task to db
                # create the data_file fil
                task = SpiderTask.objects.create(
                    date=date,
                    country=country,
                    total_page=total_page,
                    username=username,
                    password=password,
                    current_page=1,
                    done=False,
                    timestamp=int(time()),
                )
                task.save(force_insert=False, force_update=True)
                # create the data_file file for the task

                file_path = f"task_{task.id}.json"
                full_path = os.path.join(settings.MEDIA_RELATIVE_ROOT, file_path)

                task.data_file_path = full_path

                # here we will start one thread to do the task, the task is from the current_page to total_page, by the spider_logic.spider_data function
                def run_spider(task_id):
                    task = SpiderTask.objects.get(id=task_id)
                    while task.current_page <= task.total_page and not task.stop_flag:
                        data = spider_logic.spider_data(
                            task.date, task.country, task.current_page
                        )
                        file_path = f"spider_data/task_{task.id}.json"
                        full_path = os.path.join(
                            settings.MEDIA_RELATIVE_ROOT, file_path
                        )
                        with open(full_path, "w") as f:
                            json.dump(data, f)
                        task.current_page += 1
                        task.save(force_insert=False, force_update=True)
                        logger.info(
                            f"Task {task.id} processing page {task.current_page}"
                        )
                    if task.stop_flag:
                        logger.info(f"Task {task.id} has been stopped.")
                    else:
                        task.done = True
                        task.save()
                        logger.info(f"Task {task.id} completed.")

                thread = threading.Thread(target=run_spider, args=(task.id,))
                thread.start()

                return render(
                    request,
                    "spider_app/home.html",
                    {"form": form, "error": "Task started."},
                )
            except Exception as e:
                return render(
                    request, "spider_app/home.html", {"form": form, "error": str(e)}
                )
    else:
        form = SpiderForm()
    return render(request, "spider_app/home.html", {"form": form})


def stop_task(request, task_id):
    task = get_object_or_404(SpiderTask, id=task_id)
    if not task.done and not task.stop_flag:
        task.stop_flag = True
        task.save()
        logger.info(f"Task {task.id} has been signaled to stop.")
    return redirect("tasks")  # Redirect to a page showing tasks


def tasks(request):
    tasks = SpiderTask.objects.all().order_by("-id")
    return render(request, "spider_app/task.html", {"tasks": tasks})


def download_file(request, task_id):
    task = get_object_or_404(SpiderTask, id=task_id)
    if task:
        if task.data_file_path and os.path.exists(task.data_file_path):
            file_path = task.data_file_path
            return FileResponse(
                open(file_path, "rb"),
                as_attachment=True,
                filename=os.path.basename(file_path),
            )
    return redirect("tasks")


def change_authority(request):
    result = None
    if request.method == "POST":
        form = ChangeAuthorityForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            target_username = form.cleaned_data["target_username"]
            action = request.POST.get("action")
            spider = SpiderLogic(
                {
                    "username": username,
                    "password": password,
                    "target_username": target_username,
                }
            )

            if action == "upgrade":
                # Logic to upgrade authority
                # Example: spider_logic.upgrade_role(target_username)
                spider.change_user_role(target_username)
                logger.info(f"{username} upgraded authority for {target_username}")
                result = f"{username} upgraded authority for {target_username}"
            elif action == "downgrade":
                # Logic to downgrade authority
                # Example: spider_logic.downgrade_role(target_username)
                spider.revert_normal_role()
                logger.info(f"{username} downgraded authority to normal user")
                result = f"{username} downgraded authority to normal user"
            else:
                result = "Invalid action."

    else:
        form = ChangeAuthorityForm()
    return render(
        request, "spider_app/change_authority.html", {"form": form, "result": result}
    )
