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
