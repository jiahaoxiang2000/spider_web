from django import forms
from .models import Spider


class SpiderForm(forms.ModelForm):
    class Meta:
        model = Spider
        fields = ["username", "password", "date", "country_code", "page_number"]
