from django import forms
from .models import Spider


class SpiderForm(forms.ModelForm):
    class Meta:
        model = Spider
        fields = ["username", "password", "date", "country_code", "page_number"]
        

class ChangeAuthorityForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    target_username = forms.CharField(label='Target Username', max_length=100)