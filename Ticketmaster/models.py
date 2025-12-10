from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class UserA(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)

class Events(models.Model):
    eventId = models.CharField(max_length = 20, primary_key=True)
    actName = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    stateCode = models.CharField(max_length=2)
    dateString = models.CharField(max_length=100, default='Date TBD')
    timeString = models.CharField(max_length=100, default='Time TBD')
    photo = models.URLField()
    link = models.URLField()

class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Events, on_delete=models.CASCADE)

class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Events, on_delete=models.CASCADE)
    comment = models.TextField()