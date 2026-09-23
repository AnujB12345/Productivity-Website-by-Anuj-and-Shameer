from django.db import models
from PIL import Image

class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # hashed, not plaintext
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    firstName = models.CharField(max_length=100, default="Anonymous")
    lastName = models.CharField(max_length=100, default="Anonymous")
    preferredName = models.CharField(max_length=100, default= None, blank=True, null=True)


    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # save first so the file actually exists on disk

        if self.profile_picture:
            img_path = self.profile_picture.path
            img = Image.open(img_path)

            max_size = (400, 400)

            if img.height > max_size[1] or img.width > max_size[0]:
                img.thumbnail(max_size)
                img.save(img_path)