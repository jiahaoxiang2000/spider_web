from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Spider
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
            spider_logic = SpiderLogic(spider_data)
            try:
                spider_logic.start()
                return redirect("fail")
            except Exception as e:
                return render(
                    request, "spider_app/home.html", {"form": form, "error": str(e)}
                )
    else:
        form = SpiderForm()
    return render(request, "spider_app/home.html", {"form": form})


def fail(request):
    failed_operations = Spider.objects.all()
    return render(
        request, "spider_app/fail.html", {"failed_operations": failed_operations}
    )


def spider_status(request):
    return JsonResponse({"status": SpiderLogic.status()})


def change_authority(request):
    result = None
    if request.method == "POST":
        form = ChangeAuthorityForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            target_username = form.cleaned_data["target_username"]
            # Add your logic to change the account authority here
            # For example, you can call a function to perform the operation
            logger.info(f"Authority for {target_username} changed by {username}")
            result = f"Authority for {target_username} changed by {username}"
    else:
        form = ChangeAuthorityForm()
    return render(
        request, "spider_app/change_authority.html", {"form": form, "result": result}
    )
