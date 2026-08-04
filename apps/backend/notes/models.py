from django.db import models

class Note(models.Model):
    title = models.CharField(max_length=200)
    username = models.CharField(max_length=100)
    description = models.TextField(max_length=5000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    subject = models.CharField(max_length=100, blank=True)
    subject_colour = models.CharField(max_length=7, blank=True, default="#000000")  # Default color is black

    def __str__(self):
        return self.title