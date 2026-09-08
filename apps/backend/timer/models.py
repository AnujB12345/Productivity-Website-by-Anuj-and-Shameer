from django.db import models


class PomodoroSettings(models.Model):
    username = models.CharField(max_length=100, unique=True)
    work_minutes = models.PositiveIntegerField(default=25)
    short_break_minutes = models.PositiveIntegerField(default=5)
    long_break_minutes = models.PositiveIntegerField(default=15)
    sessions_before_long_break = models.PositiveIntegerField(default=4)

    def __str__(self):
        return f"{self.username}'s Pomodoro settings"


class PomodoroSession(models.Model):
    SESSION_TYPES = [
        ("work", "Focus"),
        ("short_break", "Short break"),
        ("long_break", "Long break"),
    ]

    username = models.CharField(max_length=100)
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES, default="work")
    duration_minutes = models.PositiveIntegerField()
    task_label = models.CharField(max_length=200, blank=True)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-completed_at"]

    def __str__(self):
        return f"{self.username} - {self.get_session_type_display()} ({self.duration_minutes}m)"