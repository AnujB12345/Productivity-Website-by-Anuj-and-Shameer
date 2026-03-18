from django.db import models

# Create your models here.

# class TodoItem(models.Model):
#     title = models.CharField(max_length=200)
#     completed = models.BooleanField(default=False)

###
class React(models.Model):
    employee = models.CharField(max_length=30)
    department = models.CharField(max_length=500)

    def __str__(self):
        return self.employee
###
    

