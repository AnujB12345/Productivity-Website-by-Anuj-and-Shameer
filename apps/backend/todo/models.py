from django.db import models
from users.models import User

class Todo(models.Model):
    PRIORITY_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    checked = models.BooleanField(default=False)
    priority = models.CharField(choices=PRIORITY_CHOICES, default="Medium")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title