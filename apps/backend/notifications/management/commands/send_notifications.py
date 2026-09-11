import json
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from pywebpush import webpush, WebPushException

from notifications.models import PushSubscription, NotificationSettings
from todo.models import Todo
from calendar_app.models import CalendarEvent
from notes.models import Note


class Command(BaseCommand):
    help = "Checks each user's notification settings and sends any push notifications that are due."

    def handle(self, *args, **options):
        now = timezone.now()
        tomorrow = now.date() + timedelta(days=1)

        for user_settings in NotificationSettings.objects.exclude(frequency_hours=0):
            username = user_settings.username

            if user_settings.last_notified_at:
                hours_since = (now - user_settings.last_notified_at).total_seconds() / 3600
                if hours_since < user_settings.frequency_hours:
                    continue  # not due yet

            messages = []

            if user_settings.notify_priority_tasks:
                count = Todo.objects.filter(username=username, checkbox=False, priority=3).count()
                if count:
                    messages.append(f"You have {count} high-priority task{'s' if count != 1 else ''} still to do.")

            if user_settings.notify_upcoming_events:
                events = CalendarEvent.objects.filter(username=username, date=tomorrow)
                if events.exists():
                    titles = ", ".join(e.title for e in events[:3])
                    messages.append(f"You have an event tomorrow: {titles}")

            if user_settings.notify_revision_reminder:
                has_notes = Note.objects.filter(username=username).exists()
                recently_updated = Note.objects.filter(
                    username=username, updated_at__gte=now - timedelta(days=3)
                ).exists()
                if has_notes and not recently_updated:
                    messages.append("It's been a few days — maybe review your revision notes?")

            if not messages:
                user_settings.last_notified_at = now
                user_settings.save(update_fields=["last_notified_at"])
                continue

            payload = json.dumps({
                "title": "Productivity App",
                "body": " ".join(messages),
                "url": "/dashboard/",
            })

            for sub in PushSubscription.objects.filter(username=username):
                try:
                    webpush(
                        subscription_info={
                            "endpoint": sub.endpoint,
                            "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
                        },
                        data=payload,
                        vapid_private_key=settings.VAPID_PRIVATE_KEY,
                        vapid_claims={"sub": f"mailto:{settings.VAPID_ADMIN_EMAIL}"},
                    )
                except WebPushException as e:
                    self.stdout.write(self.style.WARNING(f"Push failed for {username}: {e}"))
                    if e.response is not None and e.response.status_code in (404, 410):
                        sub.delete()  # browser unsubscribed or endpoint expired

            user_settings.last_notified_at = now
            user_settings.save(update_fields=["last_notified_at"])

        self.stdout.write(self.style.SUCCESS("Notification check complete."))