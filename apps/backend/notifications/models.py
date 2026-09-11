from django.db import models
from users.models import User

class PushSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    endpoint = models.URLField(max_length=500, unique=True)
    p256dh = models.CharField(max_length=255)
    auth = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}'s subscription"


class NotificationSettings(models.Model):
    FREQUENCY_CHOICES = [
        (0, "Never"),
        (12, "Every 12 hours"),
        (24, "Every 24 hours"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    frequency_hours = models.PositiveIntegerField(choices=FREQUENCY_CHOICES, default=24)
    notify_priority_tasks = models.BooleanField(default=True)
    notify_upcoming_events = models.BooleanField(default=True)
    notify_revision_reminder = models.BooleanField(default=True)
    last_notified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user}'s notification settings"