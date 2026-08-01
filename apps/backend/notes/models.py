from django.db import models

class Note(models.Model):
    title = models.CharField(max_length=200)
    username = models.CharField(max_length=100)
    description = models.TextField(max_length=5000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title