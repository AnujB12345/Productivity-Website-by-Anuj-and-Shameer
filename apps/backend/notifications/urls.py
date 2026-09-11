from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    path("subscribe/", views.save_subscription, name="save_subscription"),
    path("settings/", views.notification_settings_page, name="settings_page"),
]