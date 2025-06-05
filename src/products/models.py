from django.db import models

# Create your models here.
class Product(models.Model):

    title = models.TextField()
    description = models.TextField()
    price = models.TextField()
    

def __str__(self):
    return f"{self.title} {self.description} (Price: {self.price})" #tells Django how to represent your Patient object as a string