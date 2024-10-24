from django import forms
from .models import SpiderTask


class SpiderForm(forms.ModelForm):
    class Meta:
        model = SpiderTask
        fields = ["username", "password", "date", "country"]


class ChangeAuthorityForm(forms.Form):
    username = forms.CharField(label="Username", max_length=100)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    target_username = forms.CharField(label="Target Username", max_length=100)
