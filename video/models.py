# from django.db import models

# class Video(models.Model):
#     title = models.CharField(max_length=100)
#     video = models.FileField(upload_to='videos/')

#     def __str__(self):
#         return self.title

# models.py
from django.db import models

class Video(models.Model):
    title = models.CharField(max_length=100)
    video = models.FileField(upload_to='videos/')
    uploaded = models.BooleanField(default=False)


