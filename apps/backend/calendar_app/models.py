from django.db import models
from users.models import User

# Create your models here.
class CalendarEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=500, blank=True)
    date = models.DateField()
    time = models.TimeField()

    def __str__(self):
        return self.title