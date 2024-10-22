from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Spider
from .forms import SpiderForm
from .spider_logic import SpiderLogic


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
