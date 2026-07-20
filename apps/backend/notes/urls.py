from django.urls import path
from django.contrib import admin
from . import views
from django.views.generic import TemplateView

app_name = "notes"  

urlpatterns = [
    path("", views.notes, name="notes"),
]