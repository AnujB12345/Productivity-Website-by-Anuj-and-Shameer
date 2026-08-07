from django.db import models

# Create your models here.
class CalendarEvent(models.Model):
    title = models.CharField(max_length=200)
    username = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True)
    date = models.DateField()
    time = models.TimeField()

    def __str__(self):
        return self.title