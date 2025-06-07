from django.db import models

# Create your models here.
class Product(models.Model):

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    summary = models.TextField(blank=False, null=False)
    featured = models.BooleanField()

    def __str__(self):
        return f"{self.title} {self.description} (Price: {self.price})" #tells Django how to represent your Patient object as a string