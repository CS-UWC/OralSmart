from django.db import models

# Create your models here.
class Patient(models.Model):

    CHILD_AGE = [(str(i), str(i)) for i in range(0,7)]

    name = models.CharField(max_length=100, blank=False, null=False) #max_length required for models.CharField()
    surname = models.CharField(
        max_length=100,
        blank=False,
        null=False
    )
    age = models.CharField(
        max_length=1,
        choices = CHILD_AGE,
        default ='6'
    )
    parent_id = models.CharField(
        max_length=100,
        blank=False,
        null=False
    )
    parent_contact = models.CharField(
        max_length=100,
        blank=False,
        null=False
    )

    

    def __str__(self):
        return f"{self.name} {self.surname} (Age: {self.age})" #tells Django how to represent your Patient object as a string