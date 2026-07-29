from django.urls import path
from django.contrib import admin
from . import views
from django.views.generic import TemplateView

app_name = "dashboard"  

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
]