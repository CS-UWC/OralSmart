from django.db import models

# Create your models here.
class Patient(models.Model):

    CHILD_AGE = [(str(i), str(i)) for i in range(0,7)]
    
    CHILD_GENDER = [
        ('0', 'Male'),
        ('1', 'Female'),
    ]

    name = models.CharField(
        max_length=100,
        blank=False,
        null=False
    )
    surname = models.CharField(
        max_length=100,
        blank=False,
        null=False
    )
    gender = models.CharField(
        max_length=1,
        choices = CHILD_GENDER,
        default='0'
    )
    age = models.CharField(
        max_length=1,
        choices = CHILD_AGE,
        default ='6'
    )
    parent_id = models.CharField(
        max_length=13,
        blank=False,
        null=False
    )
    parent_contact = models.CharField(
        max_length=12,
        blank=False,
        null=False
    )

    def __str__(self):
        return f"{self.name} {self.surname} (Age: {self.age})" #tells Django how to represent your Patient object as a string