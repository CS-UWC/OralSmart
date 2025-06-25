from django.db import models

# Create your models here.

class Clinic(models.Model):
    name = models.CharField(max_length=64)
    address = models.CharField(max_length=64, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    website = models.URLField(max_length=199, blank=True, null=True)
    description = models.TextField(max_length=254,blank=True, null=True)
    hours = models.CharField(max_length=64, blank=True, null=True)
    emergency = models.CharField(max_length=64, blank=True, null=True)
    #geolocation = models.CharField(max_length=64, blank=True, null=True)
    clinic_type = models.CharField(
        max_length=20, 
        choices=[('public', 'Public'), ('private', 'Private')],
        default='public'
    )


    def __str__(self):
        return self.name