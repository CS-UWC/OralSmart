from django.db import models

# Create your models here.
class Patient(models.Model):

    #CHILD_AGE = [
        #('0', '0'),
        #('1', '1'),
        #('2', '2'),
        #('3', '3'),
        #('4', '4'),
        #('5', '5'),
        #('6', '6'),
        #for ((str(i), str(i)) for i in range(0,7))
    #]

    CHILD_AGE = [(str(i), str(i)) for i in range(0,7)]

    name = models.CharField(max_length=100) #max_length required for models.CharField()
    surname = models.CharField(max_length=100)
    parent_id = models.CharField(max_length=100)

    age = models.CharField(

        max_length=1,
        choices = CHILD_AGE,
        default ='6',
    )

def __str__(self):
    return f"{self.name} {self.surname} (Age: {self.age})" #tells Django how to represent your Patient object as a string