import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from notifications.models import PushSubscription, NotificationSettings
from users.models import User


@require_POST
def save_subscription(request):
    username = request.session.get("username")
    if not username:
        return JsonResponse({"status": "error", "message": "Not logged in"}, status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error"}, status=400)

    current_user = User.objects.get(username=request.session["username"])

    endpoint = data.get("endpoint")
    keys = data.get("keys", {})
    p256dh = keys.get("p256dh")
    auth = keys.get("auth")

    if not (endpoint and p256dh and auth):
        return JsonResponse({"status": "error"}, status=400)

    PushSubscription.objects.update_or_create(
        endpoint=endpoint,
        defaults={"user": current_user, "p256dh": p256dh, "auth": auth},
    )
    NotificationSettings.objects.get_or_create(user=current_user)

    return JsonResponse({"status": "ok"})


def notification_settings_page(request):
    username = request.session.get("username")
    if not username:
        return redirect("users:login")

    current_user = User.objects.get(username=request.session["username"])
    settings_obj, _ = NotificationSettings.objects.get_or_create(user=current_user)

    if request.method == "POST":
        frequency = request.POST.get("frequency_hours")
        valid_frequencies = dict(NotificationSettings.FREQUENCY_CHOICES)
        if frequency and frequency.isdigit() and int(frequency) in valid_frequencies:
            settings_obj.frequency_hours = int(frequency)

        settings_obj.notify_priority_tasks = "notify_priority_tasks" in request.POST
        settings_obj.notify_upcoming_events = "notify_upcoming_events" in request.POST
        settings_obj.notify_revision_reminder = "notify_revision_reminder" in request.POST
        settings_obj.save()
        # return redirect("notifications:settings_page")
        return redirect("dashboard:dashboard")


    return render(request, "notification_settings_page.html", {
        "notification_settings": settings_obj,
    })