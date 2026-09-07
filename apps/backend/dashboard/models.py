# dashboard/models.py
from django.db import models

# Goal model to store user-specific goals for notes and pomodoro sessions
class Goal(models.Model):
    username = models.CharField(max_length=100, unique=True)
    notes_goal = models.PositiveIntegerField(default=5)
    pomodoro_goal = models.PositiveIntegerField(default=8)  # sessions/month target, ready for when the feature ships

    def __str__(self):
        return f"{self.username}'s goal"