from django.urls import path
from django.contrib import admin
from . import views
from django.views.generic import TemplateView

app_name="calendar"
urlpatterns = [
    path("", views.add_event, name="calendar")
]