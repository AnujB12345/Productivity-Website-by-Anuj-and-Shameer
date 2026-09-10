# dashboard/models.py
from django.db import models
from users.models import User

# Goal model to store user-specific goals for notes and pomodoro sessions
class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notes_goal = models.PositiveIntegerField(default=5)
    pomodoro_goal = models.PositiveIntegerField(default=8)  # sessions/month target, ready for when the feature ships

    def __str__(self):
        return f"{self.username}'s goal"