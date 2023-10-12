from django import forms
from .models import Product
from django.contrib.auth.models import Group
from django.forms import ModelForm
from django.forms import ClearableFileInput


class CSVImportForms(forms.Form):
    csv_file = forms.FileField()
