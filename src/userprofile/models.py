from django.db import models

from django.contrib.auth.models import User

from django.db import models

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_number = models.CharField(max_length=100)
    profession = models.CharField(max_length=100)